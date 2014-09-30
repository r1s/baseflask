import flask

from flask import flash, redirect
from flask.views import MethodView
from flask.ext.babel import gettext as _
from flask.templating import render_template


class RedirectView(MethodView):

    def get(self):
        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        return '/'


class BaseView(MethodView):

    def check_permission(self):
        return True

    def check_permission_fail(self):
        return flask.abort(403)

    def dispatch_request(self, *args, **kwargs):
        if not self.check_permission():
            return self.check_permission_fail()
        return super(BaseView, self).dispatch_request(*args, **kwargs)


class BaseEditView(BaseView):
    form_class = None
    template = None
    success_url = None
    flash = True
    _messages = {'success': _('success save'),
                 'not_success': _('form data has errors')}

    @property
    def messages(self):
        def get_messages(cls):
            result = {}
            if cls == BaseUpdateView:
                return cls._messages
            for base_cls in cls.__bases__:
                if issubclass(base_cls, BaseEditView):
                    result = get_messages(base_cls)
                    result.update(cls._messages)
                    return result
            return result

        return get_messages(self.__class__)

    def get_form_class(self):
        if self.form_class is None:
            raise NotImplementedError('Not implemented form_class or get_form_class method')
        return self.form_class

    def get_success_url(self):
        if self.form_class is None:
            raise NotImplementedError('Not implemented success_url or get_success_url method')
        return self.success_url

    def get_context_data(self, form, **kwargs):
        context = kwargs
        context.update({'form': form})
        return context

    def form_invalid(self, form, message_id='not_success'):
        if self.flash:
            flash(self.messages[message_id])
        return render_template(self.template, **self.get_context_data(form=form))

    def form_valid(self, form, message_id='success'):
        self.save_form(form)
        if self.flash:
            flash(self.messages[message_id])
        return redirect(self.get_success_url())

    def get(self):
        form_class = self.get_form_class()
        form = form_class()
        return render_template(self.template, **self.get_context_data(form=form))

    def post(self):
        form_class = self.get_form_class()
        form = form_class()
        if not form.validate_on_submit():
            return self.form_invalid(form)
        return self.form_valid(form)

    def save_form(self, form):
        raise NotImplementedError('Not implemented save_form method')


class BaseUpdateView(BaseEditView):
    pass


class BaseCreateView(BaseEditView):
    pass
