# draw.io XML Recipes — ERD / UML / ML 专业图

> 用于 draw.io 引擎。当图类型命中决策树（ERD/UML/ML）时使用。

---

## ERD (Entity-Relationship Diagram)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="ERD">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Entity: User -->
        <mxCell id="e1" value="User&#xa;&#xa;+ id: UUID (PK)&#xa;+ email: string&#xa;+ name: string&#xa;+ created_at: datetime&#xa;+ updated_at: datetime"
          style="shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;strokeColor=#6c8ebf;fillColor=#dae8fc;fontColor=#1e40af;"
          vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="200" height="140" as="geometry"/>
        </mxCell>
        <!-- Entity: Order -->
        <mxCell id="e2" value="Order&#xa;&#xa;+ id: UUID (PK)&#xa;+ user_id: UUID (FK)&#xa;+ total: decimal&#xa;+ status: enum&#xa;+ created_at: datetime"
          style="shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;strokeColor=#6c8ebf;fillColor=#dae8fc;fontColor=#1e40af;"
          vertex="1" parent="1">
          <mxGeometry x="400" y="100" width="200" height="150" as="geometry"/>
        </mxCell>
        <!-- Relationship edge -->
        <mxCell id="rel1" value="places" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#854d0e;"
          vertex="1" parent="1">
          <mxGeometry x="280" y="140" width="80" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="edge1" value="1" style="endArrow=ERmandOne;startArrow=ERmandOne;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
          edge="1" parent="1" source="e1" target="rel1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="edge2" value="N" style="endArrow=ERmandOne;startArrow=ERmandOne;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
          edge="1" parent="1" source="rel1" target="e2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**布局规则：** Entity 间距 300px，同一 group 的 Entity 垂直排列间距 200px。ER 箭头用 `ERmandOne` / `ERoneToMany`。

---

## UML Class Diagram

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="UML-Class">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Class: Animal (abstract) -->
        <mxCell id="c1" value="Animal&#xa;<<abstract>>&#xa;&#xa;- name: String&#xa;- age: int&#xa;&#xa;+ makeSound(): void&#xa;+ move(): void"
          style="swimlane;fontStyle=1;align=center;startSize=26;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#6b21a8;"
          vertex="1" parent="1">
          <mxGeometry x="100" y="60" width="220" height="160" as="geometry"/>
        </mxCell>
        <!-- Separator 1 -->
        <mxCell id="sep1" value="" style="line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=10;rotatable=0;labelPosition=left;points=[];portConstraint=eastwest;"
          vertex="1" parent="c1">
          <mxGeometry y="80" width="220" height="30" as="geometry"/>
        </mxCell>
        <!-- Separator 2 -->
        <mxCell id="sep2" value="" style="line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=10;rotatable=0;labelPosition=left;points=[];portConstraint=eastwest;"
          vertex="1" parent="c1">
          <mxGeometry y="120" width="220" height="40" as="geometry"/>
        </mxCell>
        <!-- Class: Dog extends Animal -->
        <mxCell id="c2" value="Dog&#xa;&#xa;- breed: String&#xa;&#xa;+ makeSound(): void&#xa;+ fetch(): void"
          style="swimlane;fontStyle=1;align=center;startSize=26;html=1;fillColor=#dbeafe;strokeColor=#6c8ebf;fontColor=#1e40af;"
          vertex="1" parent="1">
          <mxGeometry x="100" y="300" width="200" height="130" as="geometry"/>
        </mxCell>
        <!-- Inheritance arrow: Dog → Animal -->
        <mxCell id="inh1" value="" style="endArrow=block;endFill=0;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;strokeColor=#9673a6;"
          edge="1" parent="1" source="c2" target="c1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- Interface: Runnable -->
        <mxCell id="i1" value="«interface»&#xa;Runnable&#xa;&#xa;+ run(): void"
          style="swimlane;fontStyle=1;align=center;startSize=26;html=1;dashed=1;fillColor=#fef9c3;strokeColor=#d6b656;fontColor=#854d0e;"
          vertex="1" parent="1">
          <mxGeometry x="380" y="300" width="180" height="110" as="geometry"/>
        </mxCell>
        <!-- Implementation arrow: Dog implements Runnable -->
        <mxCell id="impl1" value="" style="endArrow=block;endFill=0;dashed=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;strokeColor=#d6b656;"
          edge="1" parent="1" source="c2" target="i1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**UML 箭头速查：**
- 继承：hollow triangle（`endArrow=block;endFill=0`）
- 实现：dashed hollow triangle
- 组合：filled diamond（`endArrow=diamondThin;endFill=1`）
- 聚合：hollow diamond（`endArrow=diamondThin;endFill=0`）
- 依赖：dashed open arrow（`dashed=1`）

---

## UML Sequence Diagram

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="Sequence">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Actor: Client -->
        <mxCell id="a1" value="Client" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#fce7d6;strokeColor=#d97757;"
          vertex="1" parent="1">
          <mxGeometry x="60" y="40" width="30" height="480" as="geometry"/>
        </mxCell>
        <!-- Actor: Server -->
        <mxCell id="a2" value="Server" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#e8f5e3;strokeColor=#7b8b5c;"
          vertex="1" parent="1">
          <mxGeometry x="260" y="40" width="30" height="480" as="geometry"/>
        </mxCell>
        <!-- Actor: DB -->
        <mxCell id="a3" value="Database" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;fillColor=#f4e4c1;strokeColor=#d97757;"
          vertex="1" parent="1">
          <mxGeometry x="460" y="40" width="30" height="480" as="geometry"/>
        </mxCell>
        <!-- Activation boxes -->
        <mxCell id="act1" value="" style="shape=umlFrame;whiteSpace=wrap;html=1;boundedLabel=1;labelPosition=center;verticalLabelPosition=top;align=left;padding=4;fillColor=none;strokeColor=#6c8ebf;"
          vertex="1" parent="1">
          <mxGeometry x="55" y="80" width="40" height="80" as="geometry"/>
        </mxCell>
        <!-- Sync message: Client → Server -->
        <mxCell id="msg1" value="POST /api/users" style="html=1;verticalAlign=bottom;endArrow=block;rounded=0;exitX=1;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.1;entryDx=0;entryDy=0;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- Activation on Server -->
        <mxCell id="act2" value="" style="shape=umlFrame;whiteSpace=wrap;html=1;boundedLabel=1;labelPosition=center;verticalLabelPosition=top;align=left;padding=4;fillColor=none;strokeColor=#7b8b5c;"
          vertex="1" parent="1">
          <mxGeometry x="255" y="100" width="40" height="120" as="geometry"/>
        </mxCell>
        <!-- Sync message: Server → DB -->
        <mxCell id="msg2" value="INSERT" style="html=1;verticalAlign=bottom;endArrow=block;rounded=0;dashed=1;exitX=1;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.1;entryDx=0;entryDy=0;strokeColor=#999999;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- Return: DB → Server -->
        <mxCell id="ret1" value="OK" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;rounded=0;exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=1;entryY=0.9;entryDx=0;entryDy=0;strokeColor=#999999;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- Return: Server → Client -->
        <mxCell id="ret2" value="201 Created" style="html=1;verticalAlign=bottom;endArrow=open;dashed=1;rounded=0;exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=1;entryY=0.9;entryDx=0;entryDy=0;strokeColor=#999999;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**时序图规则：**
- `shape=umlLifeline` 创建参与者的垂直生命线
- Sync message: `endArrow=block`（实线）
- Async message: `endArrow=open;dashed=1`
- Return message: `endArrow=open;dashed=1;strokeColor=#999999`（灰虚线）
- Activation box: `shape=umlFrame` narrow rect

---

## ML / Deep Learning Model Diagram

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="ML-Architecture">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Input: (B, 3, 224, 224) -->
        <mxCell id="in1" value="Input&#xa;(B, 3, 224, 224)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#166534;fontColor=#166534;"
          vertex="1" parent="1">
          <mxGeometry x="40" y="200" width="120" height="60" as="geometry"/>
        </mxCell>
        <!-- Conv2D layer -->
        <mxCell id="conv1" value="Conv2D&#xa;(64, 7×7, stride=2)&#xa;+ BatchNorm + ReLU" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#1e40af;"
          vertex="1" parent="1">
          <mxGeometry x="220" y="195" width="160" height="70" as="geometry"/>
        </mxCell>
        <!-- Attention layer (purple) -->
        <mxCell id="attn1" value="Multi-Head&#xa;Self-Attention&#xa;(d_model=512)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontColor=#6b21a8;"
          vertex="1" parent="1">
          <mxGeometry x="440" y="190" width="160" height="80" as="geometry"/>
        </mxCell>
        <!-- FC / Output -->
        <mxCell id="fc1" value="Linear&#xa;(512 → num_classes)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontColor=#c2410c;"
          vertex="1" parent="1">
          <mxGeometry x="660" y="200" width="140" height="60" as="geometry"/>
        </mxCell>
        <!-- Skip connection (dashed curved arrow) -->
        <mxCell id="skip1" value="skip" style="endArrow=block;curved=1;dashed=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeColor=#9673a6;startArrow=none;"
          edge="1" parent="1" source="conv1" target="attn1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- Arrows -->
        <mxCell id="a1" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;endArrow=block;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
          edge="1" parent="1" source="in1" target="conv1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="a2" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;endArrow=block;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
          edge="1" parent="1" source="conv1" target="attn1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="a3" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;endArrow=block;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
          edge="1" parent="1" source="attn1" target="fc1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**ML 图颜色规范：**
- Input/Output: 绿色 `#dcfce7` / `#166534`
- Conv/Pooling: 蓝色 `#dae8fc` / `#6c8ebf`
- Attention/Transformer: 紫色 `#e1d5e7` / `#9673a6`
- FC/Linear: 橙色 `#ffe6cc` / `#d79b00`
- Loss/Activation: 红色 `#f8cecc` / `#b85450`
- Skip connection: dashed + curved arrow
