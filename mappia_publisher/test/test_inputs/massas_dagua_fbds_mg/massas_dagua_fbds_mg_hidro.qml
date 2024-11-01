<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" labelsEnabled="0" simplifyAlgorithm="0" simplifyLocal="1" simplifyMaxScale="1" simplifyDrawingHints="1" hasScaleBasedVisibilityFlag="0" version="3.10.6-A Coruña" styleCategories="AllStyleCategories" simplifyDrawingTol="1" minScale="1e+08" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" type="categorizedSymbol" forceraster="0" enableorderby="0" attr="HIDRO">
    <categories>
      <category symbol="0" value="massa d'água" render="true" label="Massa d'água"/>
    </categories>
    <symbols>
      <symbol type="fill" alpha="1" force_rhr="0" name="0" clip_to_extent="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="171,208,229,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,0"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol type="fill" alpha="1" force_rhr="0" name="0" clip_to_extent="1">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="133,182,111,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="randomcolors" name="[source]"/>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory labelPlacementMethod="XHeight" opacity="1" penColor="#000000" penAlpha="255" barWidth="5" lineSizeType="MM" sizeType="MM" width="15" scaleBasedVisibility="0" scaleDependency="Area" sizeScale="3x:0,0,0,0,0,0" minScaleDenominator="0" maxScaleDenominator="1e+08" height="15" rotationOffset="270" backgroundColor="#ffffff" lineSizeScale="3x:0,0,0,0,0,0" penWidth="0" diagramOrientation="Up" minimumSize="0" enabled="0" backgroundAlpha="255">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" placement="1" zIndex="0" dist="0" priority="0" obstacle="0" showAll="1">
    <properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option type="Map" name="QgsGeometryGapCheck">
        <Option type="double" name="allowedGapsBuffer" value="0"/>
        <Option type="bool" name="allowedGapsEnabled" value="false"/>
        <Option type="QString" name="allowedGapsLayer" value=""/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <fieldConfiguration>
    <field name="GEOCODIGO">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="MUNICIPIO">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="UF">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="HIDRO">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NATUREZA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="RIO">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="SETOR">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="GEOCODIGO" name="" index="0"/>
    <alias field="MUNICIPIO" name="" index="1"/>
    <alias field="UF" name="" index="2"/>
    <alias field="HIDRO" name="" index="3"/>
    <alias field="NATUREZA" name="" index="4"/>
    <alias field="RIO" name="" index="5"/>
    <alias field="SETOR" name="" index="6"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="GEOCODIGO" applyOnUpdate="0"/>
    <default expression="" field="MUNICIPIO" applyOnUpdate="0"/>
    <default expression="" field="UF" applyOnUpdate="0"/>
    <default expression="" field="HIDRO" applyOnUpdate="0"/>
    <default expression="" field="NATUREZA" applyOnUpdate="0"/>
    <default expression="" field="RIO" applyOnUpdate="0"/>
    <default expression="" field="SETOR" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="GEOCODIGO" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="MUNICIPIO" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="UF" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="HIDRO" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="NATUREZA" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="RIO" exp_strength="0"/>
    <constraint unique_strength="0" constraints="0" notnull_strength="0" field="SETOR" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="GEOCODIGO"/>
    <constraint exp="" desc="" field="MUNICIPIO"/>
    <constraint exp="" desc="" field="UF"/>
    <constraint exp="" desc="" field="HIDRO"/>
    <constraint exp="" desc="" field="NATUREZA"/>
    <constraint exp="" desc="" field="RIO"/>
    <constraint exp="" desc="" field="SETOR"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column type="field" hidden="0" name="GEOCODIGO" width="-1"/>
      <column type="field" hidden="0" name="MUNICIPIO" width="-1"/>
      <column type="field" hidden="0" name="UF" width="-1"/>
      <column type="field" hidden="0" name="HIDRO" width="-1"/>
      <column type="field" hidden="0" name="NATUREZA" width="-1"/>
      <column type="field" hidden="0" name="RIO" width="-1"/>
      <column type="field" hidden="0" name="SETOR" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- código: utf-8 -*-
"""
Formas QGIS podem ter uma função Python que é chamada quando o formulário é
aberto.

Use esta função para adicionar lógica extra para seus formulários.

Digite o nome da função na "função Python Init"
campo.
Um exemplo a seguir:
"""
de qgis.PyQt.QtWidgets importar QWidget

def my_form_open(diálogo, camada, feição):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="GEOCODIGO"/>
    <field editable="1" name="HIDRO"/>
    <field editable="1" name="MUNICIPIO"/>
    <field editable="1" name="NATUREZA"/>
    <field editable="1" name="RIO"/>
    <field editable="1" name="SETOR"/>
    <field editable="1" name="UF"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="GEOCODIGO"/>
    <field labelOnTop="0" name="HIDRO"/>
    <field labelOnTop="0" name="MUNICIPIO"/>
    <field labelOnTop="0" name="NATUREZA"/>
    <field labelOnTop="0" name="RIO"/>
    <field labelOnTop="0" name="SETOR"/>
    <field labelOnTop="0" name="UF"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>HIDRO</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
