"""Comandos de domínio de estoque.

Toda mutação de ``SaldoEstoque`` passa por este módulo.
"""

from decimal import Decimal

from django.db import transaction

from apps.core.exceptions import ConflitoDominio, DadosInvalidos
from apps.estoque.models import SaldoEstoque


@transaction.atomic
def reservar_saldos_para_autorizacao(*, itens: list[dict[str, object]]) -> None:
    """Reserva saldo integral para autorização de requisição.

    ``itens`` deve conter ``material_id`` e ``quantidade_solicitada`` por item.
    A função trava saldos afetados em ordem determinística e só grava após
    validar todos os itens.
    """
    if not itens:
        raise DadosInvalidos(
            'A requisição precisa ter ao menos um item para autorizar.',
            code='sem_itens',
        )

    material_ids: list[int] = []
    quantidade_por_material: dict[int, Decimal] = {}
    for item in itens:
        try:
            material_id = int(item['material_id'])
            quantidade = Decimal(str(item['quantidade_solicitada']))
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            raise DadosInvalidos(
                'Item inválido para reserva de estoque.',
                code='item_invalido',
            ) from exc

        if quantidade <= 0:
            raise DadosInvalidos(
                'Quantidade solicitada deve ser maior que zero.',
                code='quantidade_invalida',
            )

        material_ids.append(material_id)
        quantidade_por_material[material_id] = quantidade

    saldos = list(
        SaldoEstoque.objects.select_for_update()
        .select_related('estoque', 'material')
        .filter(material_id__in=material_ids)
        .order_by('estoque_id', 'material_id', 'id')
    )

    saldo_por_material: dict[int, SaldoEstoque] = {}
    for saldo in saldos:
        saldo_por_material.setdefault(saldo.material_id, saldo)

    for material_id, quantidade in quantidade_por_material.items():
        saldo = saldo_por_material.get(material_id)
        if saldo is None:
            raise ConflitoDominio(
                'Saldo de estoque não encontrado para um dos materiais.',
                code='saldo_nao_encontrado',
            )
        if not saldo.material.ativo:
            raise ConflitoDominio(
                f"Material '{saldo.material.nome}' está inativo.",
                code='material_inativo',
            )
        if saldo.divergente:
            raise ConflitoDominio(
                f"Saldo de estoque divergente para '{saldo.material.nome}'.",
                code='saldo_divergente',
            )
        if saldo.saldo_disponivel < quantidade:
            raise ConflitoDominio(
                f"Saldo insuficiente para reservar '{saldo.material.nome}'.",
                code='saldo_insuficiente',
            )

    for material_id, quantidade in quantidade_por_material.items():
        saldo = saldo_por_material[material_id]
        saldo.saldo_reservado = saldo.saldo_reservado + quantidade
        saldo.save(update_fields=['saldo_reservado'])
