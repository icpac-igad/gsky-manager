<wps:Output>
<ows:Identifier>{{layer.name}}</ows:Identifier>
<ows:Title>{{layer.title}}</ows:Title>
<ows:Abstract>{{layer.title}}</ows:Abstract>
<wps:Data>
<wps:ComplexData mimeType="application/vnd.terriajs.catalog-member+json" schema="https://tools.ietf.org/html/rfc7159">
<![CDATA[{ "data": "date,{{layer.variable}}\n{% verbatim %}{{ . }}{% endverbatim %}"}]]>
</wps:ComplexData>
</wps:Data>
</wps:Output>