# ATK Connect 命令参考

## 概述

Connect 命令是 ATK 提供的一种文本命令接口，通过 TCP 连接发送命令字符串来操作 ATK 内部对象。

## 命令格式

### 基本格式

```
Command <ApplicationPath> <ObjectPath> {Parameters}
```

### 参数分隔符

命令参数使用空格分隔，字符串参数使用引号：

```
SetValue */Satellite/Sat1 "Propagator" Astromaster
SetAnalysisTimePeriod * "1 Nov 2007 01:02:00.00" "1 Nov 2007 03:04:00.00"
```

## 场景命令

### New — 新建场景或对象

```connect
New <ApplicationPath> <ClassPath> <NewObjectName> {NewOptions}
```

| 选项 | 说明 |
|------|------|
| `NoDefault` | 不创建默认子对象 |
| `Ignore` | 忽略错误 |
| `CentralBody <CBName>` | 指定中心天体 |

**示例**：
```connect
New / Scenario Scenario1                    # 新建场景
New / */Satellite Satellite1                # 新建卫星
New / */Facility GroundStation CentralBody Earth  # 新建地面站
New / */Satellite/Satellite1/Sensor Sensor1 # 新建卫星下传感器
New / */Facility/GroundStation/Sensor Sensor1  # 新建地面站下传感器
New / */Constellation/MyConstellation       # 新建星座容器
```

### Save / SaveAs — 保存场景

```connect
Save <ApplicationPath> <ObjectPath> ["<SaveInDirectory>"]
SaveAs <ApplicationPath> <ObjectPath> "<FilePath>"
```

**示例**：
```connect
Save / *                                   # 保存当前场景
SaveAs / * "C:/Users/Desktop/TestScen.xml"  # 另存为
```

### Load — 加载场景

```connect
Load <ApplicationPath> {<ClassPath> | VDF} "<FilePath>"
```

**示例**：
```connect
Load / Scenario "E:/ATK/Scenario1.xml"    # 加载场景文件
```

### Unload — 卸载对象或场景

```connect
Unload <ApplicationPath> <ObjectPath>
```

**示例**：
```connect
Unload / */Satellite/Satellite1             # 删除卫星
Unload / *                                  # 关闭场景
```

### SetAnalysisTimePeriod — 设置分析时段

```connect
SetAnalysisTimePeriod <ScenarioPath> {TimeInterval}
```

**示例**：
```connect
SetAnalysisTimePeriod * "1 Nov 2007 01:02:00.00" "1 Nov 2007 03:04:00.00"
```

!!! note "SDK 提示"
    `set_analysis_period()` 方法在设置时段后自动发送 `Animate * Reset` 重置动画时间线。

### SetAnalysisMode — 设置分析模式

```connect
SetAnalysisMode <ScenarioPath> "<Mode>"
```

**模式**：`Keplerian`、`Spice`、`Fixed`

**示例**：
```connect
SetAnalysisMode */Scenario/Scenario1 "Keplerian"
```

## 仿真控制命令

### Animate — 仿真控制

```connect
Animate <ScenarioPath> {AnimateOption} <Parameters>
```

| 选项 | 说明 |
|------|------|
| `Start` / `Forward` | 开始正向仿真 |
| `Reverse` | 反向仿真 |
| `Pause` / `Stop` | 暂停/停止仿真 |
| `Reset` | 重置仿真 |
| `Faster` | 加速 |
| `Slower` | 减速 |

**示例**：
```connect
Animate * Start                            # 开始仿真
Animate * Pause                            # 暂停
Animate * Reset                            # 重置
Animate * Forward                          # 正向播放
Animate * Reverse                          # 反向播放
```

### SetAnimation — 设置仿真参数

```connect
SetAnimation <ScenarioPath> {AnimateOption} <Parameters>
```

| 选项 | 说明 |
|------|------|
| `CurrentTime <TimeInstant>` | 设置当前时间 |
| `AnimationMode {Normal\|RealTime\|XRealTime}` | 设置仿真模式 |
| `TimeStep <Value>` | 设置步长 |

**示例**：
```connect
SetAnimation * AnimationMode XRealTime     # 设置为倍率模式
SetAnimation * TimeStep 60                 # 设置步长为 60 秒
```

### Window2D / Window3D — 图形窗口

```connect
Window2D <ScenarioPath> "<WindowName>"
Window3D <ScenarioPath> "<WindowName>"
```

**示例**：
```connect
Window2D */Scenario/Scenario1 "2D View"
Window3D */Scenario/Scenario1 "3D View"
```

## 卫星命令

### SetPropagator — 设置传播器

```connect
SetPropagator <SatellitePath> <PropagatorName>
```

**可用传播器**：

| 传播器 | 说明 |
|--------|------|
| `TwoBody` | 二体问题 |
| `J2Perturbation` | J2 摄动 |
| `J4Perturbation` | J4 摄动 |
| `HPOP` | 高精度轨道传播器 |
| `SGP4` | SGP4（通过 TLE） |
| `Astromaster` | Astromaster |
| `LOP` | 长期轨道预报 |
| `Vinti` | Vinti |
| `Ballistic` | 弹道 |
| `GreatArc` | 大弧段 |
| `SimpleAscent` | 简单上升段 |
| `STKExternal` | STK 外部文件 |

**示例**：
```connect
SetPropagator */Satellite/Satellite1 Astromaster
SetPropagator */Satellite/Satellite1 TwoBody
```

### SetState — 设置轨道状态

```connect
SetState <SatellitePath> <StateType> <Parameters>
```

**开普勒根数格式**：
```connect
SetState */Satellite/Sat1 Classical TwoBody "1 Jan 2024 00:00:00.000" "1 Jan 2024 00:00:00.000" 60 J2000 "1 Jan 2024 00:00:00.000" 7100 0.001 30 0 0 0
```

参数格式：
```
Classical <Propagator> "<epoch>" "<stop>" <Step> <CoordSys> "<epoch>" <SMA> <ECC> <INC> <RAAN> <ARGP> <TA>
```

**笛卡尔坐标格式**：
```connect
SetState */Satellite/Sat1 Cartesian TwoBody "1 Jan 2024 00:00:00.000" "1 Jan 2024 00:00:00.000" 60 J2000 "1 Jan 2024 00:00:00.000" x y z vx vy vz
```

**TLE 格式**：
```connect
SetState */Satellite/Sat1 TLE "<Line1>" "<Line2>"
```

!!! note "传播器限制"
    `Classical` 和 `Cartesian` 格式仅支持以下传播器：`TwoBody`、`J2Perturbation`、`J4Perturbation`、`HPOP`、`LOP`。TLE 格式自动使用 SGP4 传播器。

### SetAttitude — 设置姿态

```connect
SetAttitude <SatellitePath> "<Type>" <q1> <q2> <q3> <q4>
```

**姿态类型**：`CBF`、`J2000`、`NV`、`TLE`

**示例**：
```connect
SetAttitude */Satellite/Sat1 "J2000" 0 0 0 1
```

### SetValue — 设置属性值

```connect
SetValue <ObjectPath> "<PropertyPath>" <Value>
```

**示例**：
```connect
SetValue */Satellite/Sat1 "MainSequence.SegmentList.Initial_State.InitialState.Keplerian.sma" 7100
SetValue */Satellite/Sat1 "MassProperties.TotalMass" 500
SetValue */Satellite/Sat1 "MassProperties.DryMass" 400
SetValue */Satellite/Sat1 "MassProperties.WetMass" 500
```

### Graphics — 图形设置

```connect
Graphics <ObjectPath> SetColor <ColorIndex>
```

**示例**：
```connect
Graphics */Satellite/Sat1 SetColor 12
Graphics */Facility/Station1 SetColor 5
```

## 地面站命令

### SetPosition — 设置地面站位置

```connect
SetPosition <FacilityPath> Geodetic <Lat> <Lon> <Height>
```

参数说明：

| 参数 | 单位 | 范围 |
|------|------|------|
| Lat | 度 | -90 ~ +90 |
| Lon | 度 | -180 ~ +180 |
| Height | 米 | ≥ 0 |

**示例**：
```connect
SetPosition */Facility/Beijing Geodetic 39.9 116.4 50
```

## 传感器命令

### Define — 定义传感器视场

```connect
Define <SensorPath> Conical <ElStart> <ElEnd> <AzStart> <AzEnd>
```

**示例**：
```connect
Define */Facility/Beijing/Sensor/Sensor1 Conical 5 85 0 360
```

### Point — 设置传感器指向

```connect
Point <SensorPath> Fixed Euler <Sequence> <A1> <A2> <A3>
```

**示例**：
```connect
Point */Facility/Beijing/Sensor/Sensor1 Fixed Euler 123 180 0 0
```

### SetConstraint — 设置传感器约束

```connect
SetConstraint <SensorPath> Range Max <MaxRange>
```

注意：`MaxRange` 单位为米。

**示例**：
```connect
SetConstraint */Facility/Beijing/Sensor/Sensor1 Range Max 2000000
```

## MCS 命令

### InsertSegment — 插入 MCS 段

```connect
InsertSegment <SatellitePath> <SegmentType> Segment_<Index>
```

**段类型**：`Initial_State`、`Propagate`、`ImpulsiveBurn`、`TargetSequence`

**示例**：
```connect
InsertSegment */Satellite/Sat1 Initial_State Segment_0
InsertSegment */Satellite/Sat1 Propagate Segment_1
InsertSegment */Satellite/Sat1 ImpulsiveBurn Segment_2
InsertSegment */Satellite/Sat1 TargetSequence Segment_3
```

### RunMCS — 运行 MCS

```connect
RunMCS <SatellitePath>
```

**示例**：
```connect
RunMCS */Satellite/Satellite1
```

### ApplyAllProfileChanges — 应用配置变更

```connect
ApplyAllProfileChanges <SatellitePath>
```

**示例**：
```connect
ApplyAllProfileChanges */Satellite/Satellite1
```

### ResetAllProfiles — 重置配置

```connect
ResetAllProfiles <SatellitePath>
```

**示例**：
```connect
ResetAllProfiles */Satellite/Satellite1
```

## 报告命令

### QuickReport — 快速报告

```connect
QuickReport_<Style> <ObjectPath> {TimePeriod}
```

SDK 内部将报告样式名中的空格移除后拼接为命令名。例如样式 `"Position"` 对应命令 `QuickReport_Position`。

**常见样式**：

| 样式名 | 命令 | 说明 |
|--------|------|------|
| `Position` | `QuickReport_Position` | 位置和速度 |
| `Keplerian` | `QuickReport_Keplerian` | 开普勒根数 |
| `J2000Position` | `QuickReport_J2000Position` | J2000 位置 |
| `J2000PositionVelocity` | `QuickReport_J2000PositionVelocity` | J2000 位置速度 |
| `LLA` | `QuickReport_LLA` | 经纬高 |
| `Access` | `QuickReport_Access` | 可见性 |
| `AER` | `QuickReport_AER` | 方位角/俯仰角/距离 |

**示例**：
```connect
QuickReport_Position */Satellite/Sat1 *
QuickReport_Keplerian */Satellite/Sat1 "1 Jan 2024 00:00:00.000" "7 Jan 2024 00:00:00.000"
```

### Report_RM — 获取数据报告

```connect
Report_RM <ObjectPath> ({Option} <Value>)...
```

| 选项 | 说明 |
|------|------|
| `Style "<ReportStyleName>"` | 报告样式名称 |
| `TimePeriod "<Start>" "<Stop>"` | 分析时段 |
| `TimeStep <Value>` | 报告步长 |

**示例**：
```connect
Report_RM */Satellite/Satellite1 Style "Position" TimePeriod "2023-07-29 09:19:01.000" "2023-07-29 10:09:38.000"
Report_RM */Satellite/Satellite1 Style "J2000 Position Velocity" TimeStep 60
```

### Access — 可见性分析

```connect
Access <ObjectPath> <AccessObjectPath> {TimePeriod <StartTime> <StopTime>}
```

**示例**：
```connect
Access */Satellite/Satellite1 */Facility/GroundStation TimePeriod "14 Mar 2024 00:00:00.000" "15 Mar 2024 00:00:00.000"
```

## 覆盖分析命令

### Cov — 覆盖配置

```connect
Cov <CovDefnObjectPath> Asset <AssetObjectPath> {Action}
Cov <CovDefnObjectPath> Facility <FacilityObjectPath> {Action}
Cov <CovDefnObjectPath> Grid "<GridType>" <LatStep> <LonStep>
Cov <CovDefnObjectPath> FOM "<FomName>"
Cov <CovDefnObjectPath> Compute {TimePeriod}
```

**示例**：
```connect
Cov */CoverageDefinition/Coverage1 Asset */Satellite/Satellite1 Assign
Cov */CoverageDefinition/Coverage1 Facility */Facility/Station1 Assign
Cov */CoverageDefinition/Coverage1 Grid "LatLon" 1.0 1.0
Cov */CoverageDefinition/Coverage1 Compute *
```

### Cov_RM — 获取覆盖报告

```connect
Cov_RM <ObjectPath> Access Compute "<ReportStyle>" [{TimeIntervals}]
```

**示例**：
```connect
Cov_RM */Satellite/Satellite1 Access Compute "Coverage" "14 Mar 2024 00:00:00.000" "15 Mar 2024 00:00:00.000"
```

## 对象操作命令

### Rename — 重命名对象

```connect
Rename <ObjectPath> <NewName>
```

**示例**：
```connect
Rename */Satellite/Satellite1 Sat1
```

### Copy — 复制对象

```connect
Copy <ApplicationPath> <CopyFromObjectPath> [{CopyOption}]
```

**选项**：
- `Name <NewName>`：新对象名称
- `Path <NewObjectPath>`：新对象路径

**示例**：
```connect
Copy / Satellite/Satellite1 Name Satellite2
```

## 单位设置命令

### Units_SetConnect — 设置单位

```connect
Units_SetConnect <AppOrScenPath> {Default | {Dimension} {Unit}...}
```

**维度**：`Date`, `Distance`, `Time`, `Angle`

**示例**：
```connect
Units_SetConnect / Date JDate                        # 日期格式
Units_SetConnect / Distance km                       # 距离单位
Units_SetConnect / Time sec                          # 时间单位
```

## ATK 4.2 新增命令

以下命令在 ATK 4.2 中提供，SDK 侧对应封装见各 `atk.connect` 子模块。

### AER — 可见性视线参数报告

```connect
AER <ObjectPath> <AccessObjectPath> {TimePeriod <StartTime> <StopTime>}
```

**示例**：
```connect
AER */Satellite/Satellite1 */Facility/Station1 TimePeriod "14 Mar 2024 00:00:00.000" "15 Mar 2024 00:00:00.000"
```

### Access_RM — 获取可见性报告（9 种样式）

```connect
Access_RM <ObjectPath> Access Compute "<ReportStyle>" [{TimeIntervals} | UseObjectTimes]
```

`<ReportStyle>` 取值：`Access` / `AER` / `AER Rate` / `UnAccessible` / `UnAccessible AER` /
`Access Summary` / `AER Summary` / `UnAccessible Summary` / `Range Rate`。

**示例**：
```connect
Access_RM */Satellite/Satellite1 Access Compute "Range Rate" "14 Mar 2024 00:00:00.000" "15 Mar 2024 00:00:00.000"
```

### AccessMulti — 批量可见性（先配置后计算）

```connect
AccessMulti / Assets <AssetObjectPath>...
AccessMulti / Objects <CovObjectPath>...
AccessMulti / Access Compute [{TimeInterval} | UseObjectTimes]
```

**示例**：
```connect
AccessMulti / Assets */Satellite/Satellite1/Sensor/Sensor1 */Satellite/Satellite2/Sensor/Sensor1
AccessMulti / Objects */Facility/Target1 */Facility/Target2
AccessMulti / Access Compute "26 Sep 2035 12:00:00.00" "28 Sep 2035 12:00:00.00"
```

### Cov 族 4.2 新增子命令

```connect
Cov <CovDefnObjectPath> Interval "<Start>" "<Stop>"
Cov <ObjectPath> Access Compute [{TimeInterval} | UseObjectTimes]
Cov <ObjectPath> Access Clear
Cov_RM <CovDefnObjectPath> FOMDefine Definition <FOMType> {Parameters}
```

`Cov_RM Access` 的样式取值：`Coverage` / `Figure Of Merit` / `Satisfaction` /
`Daily Coverage` / `Coverage Gaps`。

**示例**：
```connect
Cov */CoverageDefinition/Coverage1 Interval "20 Jun 2024 04:00:00.00" "21 Jun 2024 04:00:00.00"
Cov_RM */Satellite/Satellite1 FOMDefine Definition CoverageTime Compute Total
```

### CovMulti / CovMulti_RM — 批量覆盖

```connect
CovMulti / Assets <AssetObjectPath>...
CovMulti / Objects <CovObjectPath>...
CovMulti / Access Compute [{TimeInterval} | UseObjectTimes]
CovMulti_RM / MultiFOMDefine Definition <FOMType> {Parameters}
```

**示例**：
```connect
CovMulti_RM / MultiFOMDefine Definition RevisitTime Compute maximum
```

### VectorTool — 向量几何组件

```connect
VectorTool * <ParentObject> {Create|Modify|Delete} {Kind} <Name> ["<Type>" <TypeParams>]
```

`{Kind}` 为 `Vector` / `Angle` / `Axes` / `Plane` / `Point` / `System`，
各 Kind 的合法 `<Type>` 见帮助文档 VectorTool 分页。

**示例**：
```connect
VectorTool * Satellite/Satellite1 Create Vector V1 "Displacement" "CentralBody/Earth ICRF.Origin" "CentralBody/Moon ICRF.Origin" On On Transmit "CentralBody/Earth J2000"
VectorTool * Satellite/Satellite1 Create Angle A1 "Between Vectors" "CentralBody/Earth ICRF.Axes.X" "Satellite/Satellite2 VVLH.Axes.Y"
VectorTool * Satellite/Satellite1 Delete Vector V1
```

### ACAT — 高级接近分析

```connect
New / AdvCat <Name>
ACAT <AdvCatObjPath> Threshold <DistanceValue>
ACAT <AdvCatObjPath> {Primary|Secondary} Add "<ObjPath>" Fixed <T> <C> <N> [HardBodyRadius <R>]
ACAT <AdvCatObjPath> {Primary|Secondary}Multi Add "<T1 T2 ...>" Fixed <T> <C> <N>
ACAT <AdvCatObjPath> {Primary|Secondary} Remove "<ObjPath>"
ACAT <AdvCatObjPath> {Primary|Secondary} RemoveAll
ACAT <AdvCatObjPath> TimePeriod "<Start>" "<Stop>"
ACAT <AdvCatObjPath> Compute On
ACAT <AdvCatObjPath> SSCFile {On | Off | "<FilePath>"}
```

**示例**：
```connect
ACAT */AdvCat/AdvCat1 Primary Add "Satellite/Satellite1" Fixed 21000.0 11000.0 6000.0
ACAT */AdvCat/AdvCat1 Compute On
```

### 星座创建族 — WalkerDelta / WalkerCustom / Rosette / Flower / AsymmetricFlower

```connect
WalkerDelta / Semimajoraxis <sma> Eccentricity <e> Inclination <i> RAAN <r> ArgumentOfPerigee <a> TureAnomaly <t> NumPlanes <n> NumSatsPerPlane <m> InterPlanePhaseIncrement <p> RAANSpread <r> ColorByPlane {Yes|No}
WalkerDelta <SeedPath> NumPlanes <n> NumSatsPerPlane <m> InterPlanePhaseIncrement <p> RAANSpread <r> ColorByPlane {Yes|No}
```

注意：`Semimajoraxis`、`TureAnomaly` 为 ATK 文档原文拼写（非笔误）。
其余四族命令的选项集见帮助文档对应分页。

**示例**：
```connect
WalkerDelta / Semimajoraxis 6678137 Eccentricity 0 Inclination 28.5 RAAN 0 ArgumentOfPerigee 180 TureAnomaly 180 NumPlanes 2 NumSatsPerPlane 8 InterPlanePhaseIncrement 1 RAANSpread 360 ColorByPlane Yes
Rosette */Satellite/Satellite1 NumPlanes 20 TotalNumSats 20 Molecule 1 ColorByPlane Yes
```

### QuickReportCreate / QuickReportAdd / QuickReport_RM — 快捷报告

```connect
QuickReportCreate <ScenarioPath> "<QuickReportName>"
QuickReportAdd <ScenarioPath> Name "<QuickReportName>" Type Report Style "<StyleName>" Object <TruncObjPath> [FromObject <TruncObjPath>]
QuickReport_RM <ScenarioPath> {GetList | GetReport "<QuickReportName>"}
```

**示例**：
```connect
QuickReportCreate * "J2000 Position Velocity"
QuickReportAdd * Name "Sat Pos-Vel" Type Report Style "J2000 Position Velocity" Object Satellite/Satellite1
QuickReport_RM * GetReport "Sat Pos-Vel"
```

### Exec_ReportCreate / Exec_Report_RM — 报告创建与取数

```connect
Exec_ReportCreate <ObjectPath> Style "<StyleName>" [File "<FilePath>"] [TimePeriod "<Start>" "<Stop>"] [TimeStep <Value>]
Exec_Report_RM <ObjectPath> Style "<StyleName>" [TimePeriod "<Start>" "<Stop>"] [TimeStep <Value>]
```

**示例**：
```connect
Exec_ReportCreate */Satellite/Satellite1 Style "Position" File "linshi.rsf" TimePeriod "2023-07-29 09:19:01.000" "2023-07-29 10:09:38.000"
Exec_Report_RM */Satellite/Satellite1 Style "Position" TimePeriod "2023-07-29 09:19:01.000" "2023-07-29 10:09:38.000"
```

注意：4.2.0-alpha.1 中 Exec_Report 族命令 ACK 但不返回数据（文件输出未实现）。

### InsertSegment 的 RPO 段类型

`InsertSegment` 支持 RPO 段：`SetInitialState`、`FMCircumnav`、`FMW`、`Hop`、
`PerchEqualSpacing`、`TearDrop`、`NMCircumnav`、`FollowSun`、`ExitGEO`、
`GEORendezvousDrifting`、`GEORendezvousNolead`、`HopAndStop`、`Coast`、
`GEOTargetDrift`、`NoncoplanarRendezvous`、`ConeApproach`、`CorridorApproach`、
`FastRendezvous`、`FollowSunMotion`、`GEOAltDrift`、`GEODrift`、
`GEOTargetAltDrift`、`NMCircumnavToRbar`（对应 Component 枚举 `eVASegmentRPO*`）。

**示例**：
```connect
InsertSegment */Satellite/Satellite1 ConeApproach Segment_0
```
