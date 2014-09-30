from example.forms import ExampleForm
from helpers.views import BaseView, BaseCreateView


class ExampleListView(BaseView):

    route = {'rule': 'example/',
             'name': 'example_list',
             'blueprint': 'example'}

    def get(self):
        return 'Example list'


class ExampleCreateView(BaseCreateView):

    route = {'rule': 'example/add/',
             'name': 'example_add',
             'blueprint': 'example'}

    form_class = ExampleForm

    template = 'edit.html'
