<wps:Output>
<ows:Identifier>{{layer.wps_identifier}}</ows:Identifier>
<ows:Title>{{layer.title}} Geometry Drill</ows:Title>
<ows:Abstract>{{layer.title}} Geometry Drill</ows:Abstract>
<wps:Data>
<wps:ComplexData mimeType="application/vnd.terriajs.catalog-member+json" schema="https://tools.ietf.org/html/rfc7159">
<![CDATA[{ "data": "date,{{layer.wps_tpl_cols}}\n{% verbatim %}{{ . }}{% endverbatim %}"}]]>
</wps:ComplexData>
</wps:Data>
</wps:Output>