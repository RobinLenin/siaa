class DataTableParams():
    #Filros
    draw = 0 #Contador utilizado por datatable (retorna el mismo valor que llega)
    start = 0 #Inicio de página
    length = 0 #Items por página
    search_value = '' #Texto a filtrar

    #Order
    i_order_column = 0 #Número de columna por la cual se debe ordenar
    s_order_column = 'id' #Nombre de columna a ordenar
    t_order = 'asc' #Tipo de ordenación: asc, desc
    order_column = '' #Ordenación en ORM de DJango

    #data
    total = 0 #Total de registros
    count = 0 #Número de registro que coinciden con los filtros
    items = [] #Lista de datos a mostrar (Sin aplicar formatos)
    data = [] #Lista de datos formateados

    # parameterized constructor with request.POST
    def __init__(self, request, **kwargs):
        """
        Constructor parametrizado
        :param request: Objeto request de la petición
        :param kwargs: Dict con los valores de **request.GET o **request.POST según sea el caso
        """
        self.draw = int(kwargs.get('draw', [0])[0])
        self.length = int(kwargs.get('length', [10])[0])
        self.start = int(kwargs.get('start', [0])[0])
        self.search_value = (kwargs.get('search[value]', [''])[0]).strip()

        self.i_order_column = kwargs.get('order[0][column]', [0])[0]
        self.s_order_column = kwargs.get('columns[%s][data]' % self.i_order_column, 'id')[0]

        self.t_order = kwargs.get('order[0][dir]', ['asc'])[0]

        if self.t_order == 'desc':
            self.order_column = '-' + self.s_order_column
        else:
            self.order_column = self.s_order_column
        self.request = request

        #print('kwargs: ', kwargs)
        #print('params: ', self.__dict__)

    def get_search_values(self):
        return self.search_value.split(' ')

    def init_items(self, queryset):
        self.items = queryset.order_by(self.order_column)[self.start: self.start + self.length]
        return self.items

    def result(self, data=[]):
        """
        Genar un diccionario con la data para devolver al datatable
        :param data:
        :return:
        """
        r = dict()

        if data:
            self.data = data

        r['data'] = self.data
        r['draw'] = self.draw
        r['recordsTotal'] = self.total
        r['recordsFiltered'] = self.count
        return r