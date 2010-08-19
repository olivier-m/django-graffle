# -*- coding: utf-8 -*-
#
# This file is part of Django graffle released under the BSD license.
# See the LICENSE for more information.
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.db.models import get_models
from django.template import Context

try:
    from appscript import k, app as osx_app
    from aem.findapp import ApplicationNotFoundError
except ImportError:
    raise ImportError('You should install appscript to use graffle management command.')

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--omnigraffle', action='store', dest='omnigraffle',
            default='OmniGraffle Professional 5', help='Name of your OmniGraffle App'),
    )
    help = ("Creates an OmniGraffle view of your project or app model.")
    args = "[appname]"
    label = "application name"
    
    requires_model_validation = True
    can_import_settings = True
    
    # Common properties
    _common_props = {}
    _common_props[ k.autosizing ] = k.full
    _common_props[ k.text_placement ] = k.top
    _common_props[ k.draws_stroke ] = False
    _common_props[ k.fill ] = k.linear_fill
    _common_props[ k.fill_color ] = [ 1, 1, 1 ]
    _common_props[ k.gradient_color ] = [ 0.9, 0.9, 0.9 ]
    _common_props[ k.gradient_center ] = [ 0.5, 0 ]
    _common_props[ k.magnets ] = [ [ 1, 0 ], [ -1, 0 ] ]
    
    # Table name
    _table_props = _common_props.copy()
    _table_props[ k.fill ] = None
    _table_props[ k.connect_to_group_only ] = True
    _table_props[ k.magnets ] = [[-0.73960040000000005, -1.1093999999999999], [-0.42163719999999999, -1.2649109999999999], [-3.1789149999999998e-07, -1.3333330000000001], [0.42163699999999998, -1.2649109999999999], [0.73960040000000005, -1.1093999999999999], [1.1093999999999999, -0.73960020000000004], [1.2649109999999999, -0.42163679999999998], [1.3333330000000001, 6.3578299999999997e-07], [1.2649109999999999, 0.42163780000000001], [1.1093999999999999, 0.73960060000000005], [0.73959980000000003, 1.1094010000000001], [0.42163679999999998, 1.2649109999999999], [-3.178913e-07, 1.3333330000000001], [-0.42163709999999999, 1.2649109999999999], [-0.73960000000000004, 1.1093999999999999], [-1.1093999999999999, 0.7396007], [-1.2649109999999999, 0.42163659999999997], [-1.3333330000000001, -6.3578279999999999e-07], [-1.2649109999999999, -0.42163709999999999], [-1.1094010000000001, -0.73959989999999998]]
    _table_props[ k.text ] = {
        k.text: '',
        k.font: u'Helvetica-Bold',
        k.alignment: k.center,
    }
    
    #Primary Keys
    _pkey_props = _common_props.copy()
    _pkey_props[ k.text ] = {
        k.text: '',
        k.color: [0.5,0,0],
        k.font: u'Helvetica-Bold'
    }

    #Foreign Keys
    _fkey_props = _common_props.copy()
    _fkey_props[ k.text ] = {
        k.text: '',
        k.color: [0,0.26,0]
    }

    #No Key
    _col_props = _common_props.copy()
    _col_props[ k.text ] = {
        k.text: '',
        k.color: [0,0,0]
    }
    
    #Line Properties
    _line_props = {}
    _line_props[ k.line_type ] = k.orthogonal
    _line_props[ k.corner_radius ] = 5
    _line_props[ k.stroke_color ] = [0,0.26,0]
    _line_props[ k.head_type ] = "FilledArrow"
    _line_props[ k.jump ] = True
    
    _tables = []
    _relations = []
    
    def handle(self,*args,**options):
        self.omnigraffle = options.get('omnigraffle')
        
        if len(args) == 0:
            self.apps = models.get_apps()
        else:
            self.apps = []
            for app_label in args:
                app = models.get_app(app_label)
                if not app in self.apps:
                    self.apps.append(app)
        
        self._get_models()
        self._draw_graph()
    
    def _get_models(self):
        for app in self.apps:
            for appmodel in get_models(app):
                model = self._add_model(appmodel, app)
        
        # Cleaning relations
        table_names = [x['name'] for x in self._tables]
        relations = []
        for i in self._relations:
            if i[0] in table_names and i[2] in table_names:
                relations.append(i)
        
        self._relations = relations
    
    def _add_model(self, appmodel, app):
        if hasattr(appmodel,'_meta') and appmodel._meta.proxy:
            return
        
        if appmodel.__name__ in [x['name'] for x in self._tables]:
            return
        
        abstracts = [e.__name__ for e in appmodel.__bases__ if hasattr(e, '_meta') and e._meta.abstract]
        abstract_fields = []
        for e in appmodel.__bases__:
            if hasattr(e, '_meta') and e._meta.abstract:
                abstract_fields.extend(e._meta.fields)
        model = {
            'app_name': app.__name__.replace(".", "_"),
            'name': appmodel.__name__,
            'abstracts': abstracts,
            'fields': [],
            'relations': []
        }
        
        # model attributes
        def add_attributes(field):
            model['fields'].append({
                'name': field.name,
                'type': type(field).__name__,
                'max_length': field.max_length,
                'pk': field.primary_key,
                'blank': field.blank,
                'null': field.null,
                'unique': field.unique,
                'abstract': field in abstract_fields,
            })
        
        def add_relation(field):
            if type(field).__name__ not in ('ForeignKey', 'OneToOneField', 'ManyToManyField'):
                return
            
            _rel = {
                'target_app': field.rel.to.__module__.replace('.','_'),
                'target': field.rel.to.__name__,
                'type': type(field).__name__,
                'name': field.name,
                'arrows': '',
                'needs_node': True
            }
            if _rel not in model['relations']:
                model['relations'].append(_rel)
            
            self._relations += [(model['name'], field.name, _rel['target'], field.rel.field_name)]
        
        for field in appmodel._meta.fields:
            add_attributes(field)
            add_relation(field)
        
        if appmodel._meta.many_to_many:
            for field in appmodel._meta.many_to_many:
                self._make_through_model(field)
            
        
        self._tables.append(model)
    
    def _make_through_model(self, field):
        through = field.rel.through
        if '%s' % through in [x['name'] for x in self._tables]:
            return True
        
        app = models.get_app(through._meta.app_label)
        model = self._add_model(through, app)
    
    def _draw_graph(self):
        try:
            og = osx_app(u'%s' % self.omnigraffle)
        except ApplicationNotFoundError:
            raise CommandError('Application %s could not be found' % self.omnigraffle)
        
        canvas = og.make(new=k.document).canvases[1]
        ogtables = {}
        
        for table in self._tables:
            ogtables[table['name']] = self._draw_table(og,canvas,table)
        
        for (src_table,src_field,target_table,target_field) in self._relations:
            self._draw_relation(ogtables, src_table, src_field, target_table, target_field)
        
        # Automatic layout
        canvas.layout()
    
    def _draw_table(self,og,canvas,table):
        shapes = []
        
        for field in table['fields']:
            shapes += self._draw_field(og, canvas, field)
        
        
        ogt = og.assemble(shapes, table_shape=[len(table['fields']),3])
        
        # Table subgraph with table name
        table_props = self._table_props.copy()
        table_props[ k.text ][ k.text ] = table['name']
        ogt = ogt.assemble([ogt], subgraph=True)
        ogt.background.properties.set(table_props)
        
        return ogt
    
    def _draw_field(self,og,canvas,field):
        if field['pk']:
            use_props = self._pkey_props.copy()
        elif field['type'] == 'ForeignKey':
            use_props = self._fkey_props.copy()
        else:
            use_props = self._col_props.copy()
        
        use_props[k.text][k.text] = field['name']
        field_name = canvas.graphics.end.make(new=k.shape, with_properties=use_props)
        
        field_len = ''
        if field['max_length'] is not None:
            field_len = ' (%s)' % field['max_length']
        
        use_props[k.text][k.text] = '%s%s' % (field['type'],field_len)
        field_type = canvas.graphics.end.make(new=k.shape, with_properties=use_props)
        
        field_info = self._draw_field_info(og,canvas,field)
        
        return [field_name, field_type, field_info]
    
    def _draw_field_info(self, og, canvas, field):
        p = self._col_props.copy()
        t = p[k.text] = []
        
        if field['pk']:
            t += [{k.text: u'P ', k.color: [0.50, 0, 0]}]
        else:
            if not field['null']:
                t += [{k.text: u'nn ', k.color: [0, 0.25, 0.50]}]
        
            if not field['blank']:
                t += [{k.text: u'nb ', k.color: [0, 0.25, 0.50]}]
        
            if field['unique']:
                t += [{k.text: u'u ', k.color: [0.50, 0, 0]}]
        
        c = canvas.graphics.end.make(new=k.shape, with_properties=p)
        
        return c
    
    def _draw_relation(self, ogtables, src_table, src_field, target_table, target_field):
        ogtables[src_table].connect(to=ogtables[target_table], with_properties=self._line_props)
        
        # We need to apply table props again, without text
        p = self._table_props.copy()
        del(p[k.text])
        ogtables[src_table].background.properties.set(p)
    
