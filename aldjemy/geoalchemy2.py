import geoalchemy2 as g2

def get_geo_field(geometry_type, field):
   if field.geography:
        type_class_method = g2.types.Geography
   else:
        type_class_method = g2.types.Geometry
   return type_class_method(geometry_type=geometry_type, srid=field.srid)

