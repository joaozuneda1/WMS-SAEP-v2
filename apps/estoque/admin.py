from django.contrib import admin

from apps.estoque.models import (
    Material,
    Estoque,
    SaldoEstoque,
    SaidaExcepcional,
    ItemSaidaExcepcional,
    SequenciaSaidaExcepcional,
    ImportacaoSCPI,
    MovimentacaoEstoque,
)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'unidade', 'ativo')
    list_filter = ('unidade', 'ativo')
    search_fields = ('codigo', 'nome')
    ordering = ('nome',)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        _initial_ativo = obj.ativo if (obj and obj.pk) else True

        class MaterialFormComValidacao(Form):
            def __init__(inner, *args, **kw):
                super().__init__(*args, **kw)
                inner._request = request
                inner._initial_ativo = _initial_ativo

            def clean(inner):
                cleaned_data = super().clean()
                deve_desativar = (
                    inner.instance.pk
                    and not inner.errors
                    and 'ativo' in inner.changed_data
                    and not cleaned_data.get('ativo')
                    and inner._initial_ativo
                )
                if deve_desativar:
                    from apps.core.exceptions import ErroDominio, PermissaoNegada
                    from apps.estoque.services import desativar_material

                    try:
                        desativar_material(
                            ator_id=inner._request.user.pk,
                            material_id=inner.instance.pk,
                        )
                    except PermissaoNegada as exc:
                        from django.core.exceptions import PermissionDenied

                        raise PermissionDenied(str(exc)) from exc
                    except ErroDominio as exc:
                        from django import forms

                        raise forms.ValidationError(str(exc)) from exc
                return cleaned_data

        MaterialFormComValidacao.__name__ = Form.__name__
        MaterialFormComValidacao.__qualname__ = Form.__qualname__
        return MaterialFormComValidacao

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied(
            "Materiais não podem ser excluídos. Use o campo 'ativo' para desativar."
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome')
    ordering = ('nome',)


@admin.register(SaldoEstoque)
class SaldoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'estoque',
        'material',
        'saldo_fisico',
        'saldo_reservado',
        'saldo_disponivel',
        'divergente',
    )
    list_filter = ('estoque', 'material')
    search_fields = ('estoque__nome', 'material__nome', 'material__codigo')
    ordering = ('estoque', 'material')
    readonly_fields = ('saldo_disponivel', 'divergente')


class ItemSaidaExcepcionalInline(admin.TabularInline):
    model = ItemSaidaExcepcional
    extra = 1


@admin.register(SaidaExcepcional)
class SaidaExcepcionalAdmin(admin.ModelAdmin):
    list_display = (
        'numero_publico',
        'estoque',
        'registrado_por',
        'criado_em',
        'estado',
    )
    list_filter = ('estado', 'estoque', 'criado_em')
    search_fields = ('numero_publico', 'estoque__nome')
    ordering = ('-criado_em',)
    inlines = [ItemSaidaExcepcionalInline]


@admin.register(SequenciaSaidaExcepcional)
class SequenciaSaidaExcepcionalAdmin(admin.ModelAdmin):
    list_display = ('ano', 'ultimo_numero')
    ordering = ('-ano',)


@admin.register(ImportacaoSCPI)
class ImportacaoSCPIAdmin(admin.ModelAdmin):
    list_display = (
        'arquivo_nome',
        'estoque',
        'importado_por',
        'importado_em',
        'status',
        'total_novos',
    )
    list_filter = ('status', 'estoque', 'importado_em')
    search_fields = ('arquivo_nome', 'estoque__nome')
    ordering = ('-importado_em',)
    readonly_fields = ('arquivo_hash', 'importado_em')


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'tipo',
        'material',
        'estoque',
        'delta_fisico',
        'delta_reservado',
        'criado_em',
    )
    list_filter = ('tipo', 'estoque', 'criado_em')
    search_fields = ('material__nome', 'material__codigo')
    ordering = ('-criado_em',)
    readonly_fields = ('criado_em',)
