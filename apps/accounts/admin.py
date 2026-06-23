from django.contrib import admin

from apps.accounts.models import Setor, User, VinculoAuxiliar


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'classificacao', 'chefe', 'ativo')
    list_filter = ('classificacao', 'ativo')
    search_fields = ('codigo', 'nome')
    ordering = ('nome',)

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)

        class SetorFormComValidacao(Form):
            def __init__(inner, *args, **kw):
                super().__init__(*args, **kw)
                inner._request = request

            def clean(inner):
                cleaned_data = super().clean()
                novo_chefe = cleaned_data.get('chefe')
                deve_trocar = (
                    inner.instance.pk
                    and not inner.errors
                    and 'chefe' in inner.changed_data
                    and novo_chefe is not None
                )
                if deve_trocar:
                    from apps.accounts.services import trocar_chefe_setor
                    from apps.core.exceptions import ErroDominio, PermissaoNegada

                    try:
                        trocar_chefe_setor(
                            ator_id=inner._request.user.pk,
                            setor_id=inner.instance.pk,
                            novo_chefe_id=novo_chefe.pk,
                        )
                    except PermissaoNegada as exc:
                        from django.core.exceptions import PermissionDenied

                        raise PermissionDenied(str(exc)) from exc
                    except ErroDominio as exc:
                        from django import forms

                        raise forms.ValidationError(str(exc)) from exc
                return cleaned_data

        SetorFormComValidacao.__name__ = Form.__name__
        SetorFormComValidacao.__qualname__ = Form.__qualname__
        return SetorFormComValidacao

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome', 'email', 'setor', 'is_active', 'is_staff')
    list_filter = ('setor', 'is_active', 'is_staff')
    search_fields = ('matricula', 'nome', 'email')
    ordering = ('nome',)
    fieldsets = (
        (None, {'fields': ('matricula', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'email', 'setor')}),
        (
            'Permissões',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)
        _initial_ativo = obj.is_active if (obj and obj.pk) else True

        class UserFormComValidacao(Form):
            def __init__(inner, *args, **kw):
                super().__init__(*args, **kw)
                inner._request = request
                inner._initial_ativo = _initial_ativo

            def clean(inner):
                cleaned_data = super().clean()
                deve_desativar = (
                    inner.instance.pk
                    and not inner.errors
                    and 'is_active' in inner.changed_data
                    and not cleaned_data.get('is_active')
                    and inner._initial_ativo
                )
                if deve_desativar:
                    from apps.accounts.services import desativar_usuario
                    from apps.core.exceptions import ErroDominio, PermissaoNegada

                    try:
                        desativar_usuario(
                            ator_id=inner._request.user.pk,
                            usuario_id=inner.instance.pk,
                        )
                    except PermissaoNegada as exc:
                        from django.core.exceptions import PermissionDenied

                        raise PermissionDenied(str(exc)) from exc
                    except ErroDominio as exc:
                        from django import forms

                        raise forms.ValidationError(str(exc)) from exc
                return cleaned_data

        UserFormComValidacao.__name__ = Form.__name__
        UserFormComValidacao.__qualname__ = Form.__qualname__
        return UserFormComValidacao

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(VinculoAuxiliar)
class VinculoAuxiliarAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'setor', 'ativo', 'criado_em')
    list_filter = ('ativo', 'setor')
    search_fields = ('usuario__nome', 'setor__nome')
    ordering = ('-criado_em',)

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)

        class VinculoFormComValidacao(Form):
            def __init__(inner, *args, **kw):
                super().__init__(*args, **kw)
                inner._request = request

            def clean(inner):
                cleaned_data = super().clean()
                if not inner.errors and 'ativo' in inner.changed_data:
                    from apps.accounts.services import (
                        ativar_vinculo_auxiliar,
                        desativar_vinculo_auxiliar,
                    )
                    from apps.core.exceptions import ErroDominio, PermissaoNegada

                    novo_ativo = cleaned_data.get('ativo')
                    try:
                        if novo_ativo:
                            usuario = cleaned_data.get('usuario')
                            setor = cleaned_data.get('setor')
                            ativar_vinculo_auxiliar(
                                ator_id=inner._request.user.pk,
                                usuario_id=usuario.pk,
                                setor_id=setor.pk,
                            )
                        elif inner.instance.pk:
                            desativar_vinculo_auxiliar(
                                ator_id=inner._request.user.pk,
                                vinculo_id=inner.instance.pk,
                            )
                    except PermissaoNegada as exc:
                        from django.core.exceptions import PermissionDenied

                        raise PermissionDenied(str(exc)) from exc
                    except ErroDominio as exc:
                        from django import forms

                        raise forms.ValidationError(str(exc)) from exc
                return cleaned_data

        VinculoFormComValidacao.__name__ = Form.__name__
        VinculoFormComValidacao.__qualname__ = Form.__qualname__
        return VinculoFormComValidacao

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
