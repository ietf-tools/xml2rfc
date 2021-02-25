
# imported as wp

'''
Elements not allowed in SVG 1.2:
    https://www.ruby-forum.com/topic/144684
    http://inkscape.13.x6.nabble.com/SVG-Tiny-td2881845.html
  marker
  clipPath

style properties come from the CSS, they are allowed in Tiny 1.2

DrawBerry produces attributes with inkscape:,    
'http://www.w3.org/XML/1998/namespace',  # wordle uses this

   e.g. inkscape:label and inkscape:groupmode
DrawBerry and Inkscape seem to use this for layers; don't use it!

XML NameSpaces.  Specified by xmlns attribute,
  e.g. xmlns:inkscape="http://inkscape..." specifies inkscape elements
such elements are prefixed by the namespace identifier,
  e.g. inkscape:label="Background" inkscape:groupmode="layer"

Attributes in elements{} 'bottom lines' added during chek.py testing
'''

elements = {
    'svg':            ('version', 'baseProfile', 'width', 'viewBox',
                           'preserveAspectRatio', 'snapshotTime',
                           'height', 'id', 'role'),
    'g':              ( 'label', 'class',
                           'id', 'role', 'fill', 'style', 'transform'),
    'defs':           (    'id', 'role', 'fill'),
    'title':          (    'id', 'role'),
    'desc':           (    'id', 'role'),
    'a':              (    'id', 'role', 'fill', 'transform'),  # Linking
    'use':            ('x', 'y', 'href', 'xlink:href',
                           'id', 'role',  'fill', 'transform'),
    'rect':           ('x', 'y', 'width', 'height', 'rx', 'ry',
                            'stroke-miterlimit',
                           'id', 'role', 'fill', 'style','transform'),
    'circle':         ('cx', 'cy', 'r',
                           'id', 'role', 'fill', 'style', 'transform'),
    'ellipse':        ('cx', 'cy', 'rx', 'ry',
                           'id', 'role', 'fill', 'style', 'transform'),
    'line':           ('x1', 'y1', 'x2', 'y2',
                           'id', 'role', 'fill', 'transform'),
    'polyline':       ('points',
                           'id', 'role', 'fill', 'transform'),
    'polygon':        ('points',
                           'id', 'role', 'fill', 'style', 'transform'),
    'text':           ('x', 'y', 'rotate', 'space',
                           'id', 'role', 'fill', 'style', 'transform'),
    'tspan':          ('x', 'y', 'id', 'role', 'fill'),
    
    'textArea':       ('x', 'y', 'width', 'height', 'auto',
                           'id', 'role', 'fill', 'transform'),
    'tbreak':         (
                           'id', 'role'),
    'solidColor':     (    'id', 'role', 'fill'),
    'linearGradient': ('gradientUnits', 'x1', 'y1', 'x2', 'y2',
                           'id', 'role', 'fill'),
    'radialGradient': ('gradientUnits', 'cx', 'cy', 'r',
                           'id', 'role', 'fill'),
    'stop':           (    'id', 'role', 'fill'),  # Gradients
    
    'path':           ('d', 'pathLength', 'stroke-miterlimit',
                           'id', 'role', 'fill', 'style', 'transform'),
    }

# Elements have a list of attributes (above),
#   need to know what attributes each can have.

# Properties capture CSS info, they have lists of allowable values. 
# Attributes have allowed values too;
#   we also need to know which elements they're allowed in.

properties = {
    'stroke':                ('<paint>', 'none'),  # Change from I-D 
    'stroke-width':          (),
    'stroke-linecap':        ('butt', 'round', 'square'),
    'stroke-linejoin':       ('miter', 'round', 'bevel'),
    'stroke-mitrelimit':     (),
    'stroke-dasharray':      (),
    'stroke-dashoffset':     (),
    'stroke-opacity':        (),
    'vector-effect':         ('non-scaling-stroke', 'none'),
    'viewport-fill':         ('none', 'currentColor'),
    'viewport-fill-opacity': (),

    'display':       ('inline', 'block', 'list-item', 'run-in', 'compact',
                      'marker', 'table', 'inline-table', 'table-row-group',
                      'table-header-group', 'table-footer-group',
                      'table-row,' 'table-column-group',
	              'table-column', 'table-cell', 'table-caption',
                      'none'),
    'viewport-fill-opacity': (),
    'visibility':            ('visible', 'hidden', 'collapse'),
    'color-rendering':       ('auto', 'optimizeSpeed', 'optimizeQuality'),
    'shape-rendering':       ('auto', 'optimizeSpeed', 'crispEdges',
		              'geometricPrecision'),
    'text-rendering':        ('auto', 'optimizeSpeed', 'optimizeLegibility',
		              'geometricPrecision'),
    'buffered-rendering':    ('auto', 'dynamic', 'static'),

    'opacity':               (),
    'solid-opacity':         (),
    'solid-color':           ('currentColor', '<color>'),
    'color':                 ('currentColor', '<color>'),

    'stop-color':           ('currentColor', '<color>'),
    'stop-opacity':         (),

    'line-increment':      ('auto'),
    'text-align':          ('start', 'end', 'center'),
    'display-align':       ('auto', 'before', 'center', 'after'),

    'font-size':           (),
    'font-family':         ('serif', 'sans-serif', 'monospace'),
    'font-weight':         ('normal', 'bold', 'bolder', 'lighter', '<integer>'),
    'font-style':          ('normal', 'italic', 'oblique'),
    'font-variant':        ('normal', 'small-caps'),
    'direction':           ('ltr', 'rtl'),
    'unicode-bidi':        ('normal', 'embed', 'bidi-override'),
    'text-anchor':         ('start', 'middle', 'end'),
    'fill':                ('none', '<color>'),  # # = RGB val
    'fill-rule':           ('nonzero', 'evenodd'),
    'fill-opacity':        (),

#    'style':               ('[style]'),  # Check properties in [style]  Change from I-D
    } 

basic_types = {  # Lists of allowed values
    '<color>':   ('black', 'white', '#000000', '#FFFFFF'),
                  # 'grey', 'darkgrey', 'dimgrey', 'lightgrey',
	          # 'gray', 'darkgray', 'dimgray', 'lightgray',
                  # '#808080', '#A9A9A9', '#696969', '#D3D3D3', ,
    '<paint>':   ('<color>', 'none', 'currentColor', 'inherit'),
    '<integer>': ('+')
    }
color_default = 'black'

property_lists = {  # Lists of properties to check (for Inkscape)
    '[style]':   ('font-family', 'font-weight', 'font-style',
               'font-variant', 'direction', 'unicode-bidi', 'text-anchor',
               'fill', 'fill-rule'),
    }

xmlns_urls = (  # Whitelist of allowed URLs
    'http://www.w3.org/2000/svg',  # Base namespace for SVG
    'http://www.w3.org/1999/xlink',  # svgwrite uses this
    'http://www.w3.org/XML/1998/namespace',  # imagebot uses this
    )
