import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict


def json_to_compact_excel(json_files, output_excel):
    # 初始化所有全局变量（确保跨文件统计）
    compact_data = []  # 所有阶段数据
    target_phase_data = []  # 指定路径的阶段数据
    target_node_names = []  # 指定路径下的节点名称（用于统计）
    node_phase_map = defaultdict(set)  # 节点对应的指定路径阶段（去重）
    phase_node_counter = defaultdict(Counter)  # 指定路径-节点次数映射
    all_phase_class_counter = defaultdict(Counter)  # 所有阶段-节点类名次数映射
    all_node_classes = set()  # 所有读取到的节点类名（去重）

    # 新增：节点类名-功能描述映射字典（完全按你提供的内容）
    NODE_CLASS_DESCRIPTION = {
        "questNodeDefinition": "所有Quest节点的基类",
        "questDisableableNodeDefinition": "可禁用的节点基类",
        "questSignalStoppingNodeDefinition": "可阻断信号传播的节点基类",
        "questTypedSignalStoppingNodeDefinition": "带类型的信号阻断节点",
        "questStartEndNodeDefinition": "开始/结束节点基类",
        "questStartNodeDefinition": "Quest开始节点",
        "questEndNodeDefinition": "Quest结束节点",
        "questIONodeDefinition": "输入/输出节点基类",
        "questInputNodeDefinition": "输入节点",
        "questOutputNodeDefinition": "输出节点",
        "questGraphDefinition": "Quest图定义",
        "questSocketDefinition": "Socket定义",
        "questCharacterManagerNodeDefinition": "角色管理器主节点",
        "questCharacterManagerParameters_SetAttitudeGroupForPuppet": "设置AI态度组",
        "questCharacterManagerParameters_SetGroupsAttitude": "设置组态度",
        "questCharacterManagerParameters_SetMortality": "设置生死状态",
        "questCharacterManagerParameters_SetAnimset": "设置动画集",
        "questCharacterManagerParameters_SetLowGravity": "设置低重力",
        "questCharacterManagerParameters_EnableBumps": "启用碰撞",
        "questCharacterManagerParameters_SetStatusEffect": "设置状态效果",
        "questCharacterManagerParameters_SetReactionPreset": "设置反应预设",
        "questCharacterManagerParameters_SetGender": "设置性别",
        "questCharacterManagerParameters_SetAsCrowdObstacle": "设为人群障碍物",
        "questCharacterManagerParameters_SetProgressionBuild": "设置进度构建",
        "questCharacterManagerParameters_SetLifePath": "设置人生轨迹",
        "questCharacterManagerParameters_HealPlayer": "治疗玩家",
        "questCharacterManagerCombat_ModifyHealth": "修改生命值",
        "questCharacterManagerCombat_Kill": "杀死角色",
        "questCharacterManagerCombat_EquipWeapon": "装备武器",
        "questCharacterManagerCombat_SetWeaponState": "设置武器状态",
        "questCharacterManagerCombat_SetDeathDirection": "设置死亡方向",
        "questCharacterManagerCombat_ChangeLevel": "改变等级",
        "questCharacterManagerCombat_ManageRagdoll": "管理布娃娃系统",
        "questCharacterManagerCombat_AssignSquad": "分配小队",
        "questCharacterManagerParameters_SetCombatSpace": "设置战斗空间",
        "questCharacterManagerVisuals_ChangeEntityAppearance": "改变实体外观",
        "questCharacterManagerVisuals_PrefetchEntityAppearance": "预加载实体外观",
        "questCharacterManagerVisuals_GenitalsManager": "生殖器管理",
        "questCharacterManagerVisuals_BreastSizeController": "胸部大小控制",
        "questCharacterManagerVisuals_SetBrokenNoseStage": "设置鼻梁破损阶段",
        "questEntityManagerNodeDefinition": "实体管理器主节点",
        "questEntityManagerSetAttachment_NodeType": "设置附着",
        "questEntityManagerSetDestructionState_NodeType": "设置破坏状态",
        "questEntityManagerManageBinkComponent_NodeType": "管理Bink组件",
        "questEntityManagerSetMeshAppearance_NodeType": "设置网格外观",
        "questEntityManagerEnablePlayerTPPRepresentation_NodeType": "启用玩家第三人称表示",
        "questEntityManagerToggleComponent_NodeType": "切换组件",
        "questEntityManagerChangeAppearance_NodeType": "改变外观",
        "questEntityManagerMountPuppet_NodeType": "骑乘Puppet",
        "questEntityManagerSendAnimationEvent_NodeType": "发送动画事件",
        "questEntityManagerSetStat_NodeType": "设置属性",
        "questEntityManagerToggleMirrorsArea_NodeType": "切换镜像区域",
        "questEntityManagerSetAttachment_ToActor": "附着到角色",
        "questEntityManagerDestroyCarriedObject": "销毁携带物体",
        "questEntityManagerSetAttachment_ToNode": "附着到节点",
        "questEntityManagerSetAttachment_ToWorld": "附着到世界",
        "questUIManagerNodeDefinition": "UI管理器主节点",
        "questAddCombatLogMessage_NodeType": "添加战斗日志消息",
        "questSwitchNameplate_NodeType": "切换名牌",
        "questAddBraindanceClue_NodeType": "添加脑舞线索",
        "questDiscoverBraindanceClue_NodeType": "发现脑舞线索",
        "questDisplayMessageBox_NodeType": "显示消息框",
        "questProgressBar_NodeType": "进度条",
        "questProximityProgressBar_NodeType": "接近度进度条",
        "questShowDialogIndicator_NodeType": "显示对话指示器",
        "questHUDVideo_NodeType": "HUD视频",
        "questSetLocationName_NodeType": "设置位置名称",
        "questWarningMessage_NodeType": "警告消息",
        "questShowOnscreen_NodeType": "屏幕显示",
        "questOverrideLoadingScreen_NodeType": "覆盖加载屏幕",
        "questGlitchLoadingScreen_NodeType": "故障加载屏幕",
        "questWaitForAnyKeyLoadingScreen_NodeType": "等待任意键加载屏幕",
        "questSetUIGameContext_NodeType": "设置UI游戏上下文",
        "questSetHUDEntryForcedVisibility_NodeType": "设置HUD条目强制可见性",
        "questQuickItemsManager_NodeType": "快速物品管理器",
        "questVendorPanel_NodeType": "商贩面板",
        "questOpenBriefing_NodeType": "打开简报",
        "questEnableBraindanceFinish_NodeType": "启用脑舞完成",
        "questSwitchToScenario_NodeType": "切换到场景",
        "questSetBriefingSize_NodeType": "设置简报大小",
        "questSetBriefingAlignment_NodeType": "设置简报对齐",
        "questShowNarrativeEvent_NodeType": "显示叙事事件",
        "questShowCustomTooltip_NodeType": "显示自定义提示",
        "questTutorial_NodeType": "教程",
        "questToggleMinimapVisibility_NodeSubType": "切换小地图可见性",
        "questToggleStealthMappinVisibility_NodeSubType": "切换潜行地图标记可见性",
        "questShowHighlight_NodeSubType": "显示高亮",
        "questShowBracket_NodeSubType": "显示括号",
        "questShowOverlay_NodeSubType": "显示覆盖层",
        "questShowPopup_NodeSubType": "显示弹出窗口",
        "questBriefingSequencePlayer_NodeType": "简报序列播放器",
        "questTriggerIconGeneration_NodeType": "触发图标生成",
        "questInputHint_NodeType": "输入提示",
        "questInputHintGroup_NodeType": "输入提示组",
        "questShowLevelUpNotification_NodeType": "显示升级通知",
        "questShowCustomQuestNotification_NodeType": "显示自定义任务通知",
        "questSetMetaQuestProgress_NodeType": "设置元任务进度",
        "questSetSaveDataLoadingScreen_NodeType": "设置存档数据加载屏幕",
        "questSetFastTravelBinksGroup_NodeType": "设置快速旅行视频组",
        "questOpenPhotoMode_NodeType": "打开照片模式",
        "questShowPointOfNoReturnPrompt_NodeType": "显示不归路提示",
        "questFinalBoardsVideosFinished_NodeType": "最终板视频完成",
        "questFinalBoardsEnableSkipCredits_NodeType": "最终板启用跳过制作人员名单",
        "questFinalBoardsOpenSpeakerScreen_NodeType": "最终板打开扬声器屏幕",
        "questVehicleNodeDefinition": "车辆管理器主节点",
        "questAssignCharacter_NodeType": "分配角色",
        "questRequestVehicleCameraPerspective_NodeType": "请求车辆相机视角",
        "questMoveOnSpline_NodeType": "在样条上移动",
        "questToggleCombatForPlayer_NodeType": "切换玩家战斗",
        "questToggleSwitchSeatsForPlayer_NodeType": "切换玩家座位",
        "questMoveOnSplineAndKeepDistance_NodeType": "在样条上移动并保持距离",
        "questMoveOnSplineControlRubberbanding_NodeType": "在样条上移动控制橡皮筋效果",
        "questStartVehicle_NodeType": "启动车辆",
        "questStopVehicle_NodeType": "停止车辆",
        "questFollowObject_NodeType": "跟随物体",
        "questResetMovement_NodeType": "重置移动",
        "questSetAutopilot_NodeType": "设置自动驾驶",
        "questToggleBrokenTire_NodeType": "切换轮胎损坏",
        "questToggleForceBrake_NodeType": "切换强制制动",
        "questFlushAutopilot_NodeType": "刷新自动驾驶",
        "questToggleTankCustomFPPLockOff_NodeType": "切换坦克自定义FPP锁定",
        "questToggleWeaponEnabled_NodeType": "切换武器启用",
        "questOverrideSplineSpeed_NodeType": "覆盖样条速度",
        "questRepair_NodeType": "修理",
        "questToggleDoor_NodeType": "切换车门",
        "questSpawnPlayerVehicle_NodeType": "生成玩家车辆",
        "questTeleport_NodeType": "传送",
        "questForbiddenTrigger_NodeType": "禁止触发器",
        "questEnableVehicleSummon_NodeType": "启用车辆召唤",
        "questEnablePlayerVehicle_NodeType": "启用玩家车辆",
        "questToggleWindow_NodeType": "切换车窗",
        "questUnassignAll_NodeType": "取消所有分配",
        "questForcePhysicsWakeUp_NodeType": "强制物理唤醒",
        "questSetImmovable_NodeType": "设置不可移动",
        "questAICommandNodeBase": "AI命令节点基类",
        "questConfigurableAICommandNode": "可配置AI命令节点",
        "questSendAICommandNodeDefinition": "发送AI命令",
        "questCombatNodeDefinition": "战斗节点",
        "questMovePuppetNodeDefinition": "移动Puppet",
        "questMiscAICommandNode": "杂项AI命令",
        "questTeleportPuppetNodeDefinition": "传送Puppet",
        "questEquipItemNodeDefinition": "装备物品",
        "questUnequipItemNodeDefinition": "卸下物品",
        "questUseWorkspotNodeDefinition": "使用工作点",
        "questRotateToNodeDefinition": "旋转到目标",
        "questVehicleNodeCommandDefinition": "车辆命令",
        "questForcedBehaviourNodeDefinition": "强制行为",
        "questClearForcedBehavioursNodeDefinition": "清除强制行为",
        "questLookAtDrivenTurnsNode": "注视驱动转向",
        "questLogicalBaseNodeDefinition": "逻辑节点基类",
        "questLogicalAndNodeDefinition": "逻辑与节点",
        "questLogicalXorNodeDefinition": "逻辑异或节点",
        "questLogicalHubNodeDefinition": "逻辑Hub节点",
        "questIBaseCondition": "条件基类接口",
        "questCondition": "条件类",
        "questTypedCondition": "带类型的条件",
        "questLogicalCondition": "逻辑条件",
        "questConditionNodeDefinition": "条件节点",
        "questPauseConditionNodeDefinition": "暂停条件节点",
        "questObjectCondition": "对象条件",
        "questInteraction_ConditionType": "交互条件",
        "questInventory_ConditionType": "库存条件",
        "questInspect_ConditionType": "检查条件",
        "questScan_ConditionType": "扫描条件",
        "questEntryScanned_ConditionType": "条目扫描条件",
        "questDevice_ConditionType": "设备条件",
        "questDestruction_ConditionType": "破坏条件",
        "questTagged_ConditionType": "标记条件",
        "questPaymentCondition": "支付条件",
        "questPaymentBalanced_ConditionType": "平衡支付条件",
        "questPaymentFixedAmount_ConditionType": "固定金额支付条件",
        "questStatsCondition": "属性条件",
        "questStat_ConditionType": "属性条件",
        "questStreetCredTier_ConditionType": "街头声望等级条件",
        "questLifePath_ConditionType": "人生轨迹条件",
        "questBuild_ConditionType": "构建条件",
        "questCameraFocus_ConditionType": "相机焦点条件",
        "questVisionMode_ConditionType": "视觉模式条件",
        "questPlatform_ConditionType": "平台条件",
        "questInputAction_ConditionType": "输入动作条件",
        "questInputController_ConditionType": "输入控制器条件",
        "questPhone_ConditionType": "电话条件",
        "questPhonePickUp_ConditionType": "电话接听条件",
        "questPrereq_ConditionType": "前置条件",
        "questWeather_ConditionType": "天气条件",
        "questRadio_ConditionType": "电台条件",
        "questRadioTrack_ConditionType": "电台曲目条件",
        "questPlaylistTrackChanged_ConditionType": "播放列表曲目变更条件",
        "questLanguage_ConditionType": "语言条件",
        "questGOGReward_ConditionType": "GOG奖励条件",
        "questSaveLock_ConditionType": "存档锁定条件",
        "questTimeCondition": "时间条件",
        "questRealtimeDelay_ConditionType": "实时延迟条件",
        "questGameTimeDelay_ConditionType": "游戏时间延迟条件",
        "questTimePeriod_ConditionType": "时间段条件",
        "questEnvironmentManagerNodeDefinition": "环境管理器主节点",
        "questPlayEnv_NodeType": "播放环境",
        "questPlayEnv_OverrideGlobalLight": "覆盖全局光照",
        "questPlayEnv_ForceRelitEnvProbe": "强制重新照明环境探针",
        "questPlayEnv_SetWeather": "设置天气",
        "questGameManagerNodeDefinition": "游戏管理器主节点",
        "questTimeDilation_World": "世界时间膨胀",
        "questTimeDilation_Player": "玩家时间膨胀",
        "questTimeDilation_Entity": "实体时间膨胀",
        "questContentTokenManager_NodeType": "内容令牌管理器",
        "questGameplayRestrictions_NodeType": "游戏限制",
        "questSetTimer_NodeType": "设置计时器",
        "questRumble_NodeType": "震动",
        "questEventManagerNodeDefinition": "事件管理器节点",
        "questFXManagerNodeDefinition": "特效管理器主节点",
        "questPlayFX_NodeType": "播放特效",
        "questPreloadFX_NodeType": "预加载特效",
        "questRenderFxManagerNodeDefinition": "渲染特效管理器主节点",
        "questSetFadeInOut_NodeType": "设置淡入淡出",
        "questSetDebugView_NodeType": "设置调试视图",
        "questSetCyberspacePostFX_NodeType": "设置赛博空间后处理",
        "questSetRenderLayer_NodeType": "设置渲染层",
        "questItemManagerNodeDefinition": "物品管理器主节点",
        "questAddRemoveItem_NodeType": "添加/移除物品",
        "questDropItemFromSlot_NodeType": "从槽位丢弃物品",
        "questSetItemTags_NodeType": "设置物品标签",
        "questTransferItem_NodeType": "转移物品",
        "questUseWeapon_NodeType": "使用武器",
        "questInjectLoot_NodeType": "注入战利品",
        "questInteractiveObjectManagerNodeDefinition": "交互对象管理器主节点",
        "questSetInteractionState_NodeType": "设置交互状态",
        "questHackingManager_NodeType": "黑客管理器",
        "questDeviceManager_NodeType": "设备管理器",
        "questTriggerManagerNodeDefinition": "触发器管理器主节点",
        "questSetTriggerState_NodeType": "设置触发器状态",
        "questJournalNodeDefinition": "日志节点主节点",
        "questJournalEntry_NodeType": "日志条目",
        "questJournalQuestEntry_NodeType": "任务日志条目",
        "questJournalTrackQuest_NodeType": "追踪任务",
        "questPhoneManagerNodeDefinition": "电话管理器主节点",
        "questAddRemoveContact_NodeType": "添加/移除联系人",
        "questSetPhoneStatus_NodeType": "设置电话状态",
        "questCallContact_NodeType": "呼叫联系人",
        "questSendMessage_NodeType": "发送消息",
        "questSceneManagerNodeDefinition": "场景管理器主节点",
        "questSetTier_NodeType": "设置Tier等级",
        "questPlayerLookAt_NodeType": "玩家注视",
        "questNPCLookAt_NodeType": "NPC注视",
        "questSetFOV_NodeType": "设置视野",
        "questAudioNodeDefinition": "音频节点主节点",
        "questAudioCharacterManagerNodeDefinition": "角色音频管理器",
        "questAudioMixNodeType": "音频混合",
        "questAudioSwitchNodeType": "音频开关",
        "questBehaviourManagerNodeDefinition": "行为管理器主节点",
        "questJumpWorkspotAnim_NodeType": "跳转工作点动画",
        "questStopWorkspot_NodeType": "停止工作点",
        "questFactsDBManagerNodeDefinition": "事实数据库管理器主节点",
        "questSetVar_NodeType": "设置变量",
        "questMapPinManagerNodeDefinition": "地图标记管理器",
        "questRewardManagerNodeDefinition": "奖励管理器主节点",
        "questGiveReward_NodeType": "给予奖励",
        "questSpawnManagerNodeDefinition": "生成管理器主节点",
        "questTimeManagerNodeDefinition": "时间管理器主节点",
        "questVisionModesManagerNodeDefinition": "视觉模式管理器主节点",
        "questVoicesetManagerNodeDefinition": "语音集管理器主节点",
        "questRecordingNodeDefinition": "录制节点主节点",
        "questFlowControlNodeDefinition": "流程控制节点",
        "questSwitchNodeDefinition": "开关节点",
        "questRandomizerNodeDefinition": "随机器节点",
        "questCheckpointNodeDefinition": "检查点节点",
        "questEmbeddedGraphNodeDefinition": "嵌入式图节点",
        "questPhaseNodeDefinition": "阶段节点",
        "questDeletionMarkerNodeDefinition": "删除标记节点",
        "questMultiplayerAIDirectorNodeDefinition": "多人游戏AI导演节点",
        "questMultiplayerChoiceTokenNodeDefinition": "多人游戏选择令牌节点",
        "questMultiplayerJunctionDialogNodeDefinition": "多人游戏交汇对话节点",
        "questMultiplayerTeleportPuppetNodeDefinition": "多人游戏传送Puppet节点",
        "questBaseObjectNodeDefinition": "基础对象节点",
        "questCutControlNodeDefinition": "剪辑控制节点",
        "questMinigameNodeDefinition": "小游戏节点",
        "questPlaceholderNodeDefinition": "占位符节点",
        "questPuppeteerNodeDefinition": "操纵者节点",
        "questPuppetAIManagerNodeDefinition": "Puppet AI管理器节点",
        "questPopulactionControllerNodeDefinition": "人口控制器节点",
        "questInstancedCrowdControlNodeDefinition": "实例化人群控制节点",
        "questTransformAnimatorNodeDefinition": "变换动画器节点",
        "questTeleportVehicleNodeDefinition": "传送车辆节点",
        "questWorkspotParamNodeDefinition": "工作点参数节点"
    }
    # 指定路径前缀
    TARGET_PATH_PREFIXES = [
        r"base\quest\main_quests",
        r"base\quest\side_quests",
        r"base\quest\minor_quests"
    ]

    # 遍历所有输入文件（修复：确保所有文件数据都被收集）高频节点路径分布（工作表4）
    for json_file in json_files:
        file_path = Path(json_file)
        if not file_path.exists():
            print(f"⚠️  {json_file} 不存在，跳过")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取 {json_file} 失败：{str(e)}，跳过该文件")
            continue

        # 第一遍循环：收集统计数据（所有文件共享全局变量）
        for phase, nodes in data.get("questphases", {}).items():
            # 收集所有阶段-节点类名数据（用于类名矩阵）
            class_counter = Counter()
            for node in nodes:
                node_class = str(node.get("class", "")).strip()
                if node_class:
                    class_counter[node_class] += 1
                    all_node_classes.add(node_class)
            all_phase_class_counter[phase] = class_counter

            # 收集指定路径下的节点名称统计（用于高频节点相关表格）
            if any(phase.startswith(prefix) for prefix in TARGET_PATH_PREFIXES):
                phase_counter = Counter()
                for node in nodes:
                    node_name = str(node.get("name", "")).strip()
                    if node_name:
                        target_node_names.append(node_name)
                        node_phase_map[node_name].add(phase)  # 自动去重
                        phase_counter[node_name] += 1
                phase_node_counter[phase] = phase_counter

        # 第二遍循环：收集阶段详情数据（用于阶段汇总表格）
        for phase, nodes in data.get("questphases", {}).items():
            # 所有阶段汇总数据
            compact_data.append({
                "阶段路径": phase,
                "节点ID集合": " | ".join(str(n.get("id", "")) for n in nodes),
                "节点名称集合": " | ".join(str(n.get("name", "")) for n in nodes),
                "节点类名集合": " | ".join(str(n.get("class", "")) for n in nodes),
                "节点路径集合": " | ".join(str(n.get("path", "")) for n in nodes),
                "节点数": len(nodes)
            })
            # 指定路径阶段汇总数据
            if any(phase.startswith(prefix) for prefix in TARGET_PATH_PREFIXES):
                target_phase_data.append({
                    "阶段路径": phase,
                    "节点ID集合": " | ".join(str(n.get("id", "")) for n in nodes),
                    "节点名称集合": " | ".join(str(n.get("name", "")) for n in nodes),
                    "节点类名集合": " | ".join(str(n.get("class", "")) for n in nodes),
                    "节点路径集合": " | ".join(str(n.get("path", "")) for n in nodes),
                    "节点数": len(nodes)
                })

    # 关键修复：所有文件处理完成后，再进行全局统计（之前缩进在文件循环内，导致统计不完整）
    name_counter = Counter(target_node_names)
    sorted_names = sorted(name_counter.items(), key=lambda x: x[1], reverse=True)
    high_freq_nodes = [name for name, cnt in name_counter.items() if cnt >= 10]

    # 打印统计结果（验证数据是否正确收集）
    print("=" * 60)
    print("📊 数据收集完成，统计摘要：")
    print(f"   - 处理文件数：{len(json_files)}")
    print(f"   - 所有阶段总数：{len(compact_data)}")
    print(f"   - 指定路径阶段数：{len(target_phase_data)}")
    print(f"   - 不同节点名称数：{len(name_counter)}")
    print(f"   - 不同节点类名数：{len(all_node_classes)}")
    print(f"   - 高频节点数（≥10次）：{len(high_freq_nodes)}")
    print("=" * 60)

    # 1. 所有阶段汇总（工作表1）
    df_all_phase = pd.DataFrame(compact_data)

    # 2. 指定路径节点统计（工作表2）
    df_node_count = pd.DataFrame([
        {"排名": idx + 1, "节点名称": name, "出现次数": cnt}
        for idx, (name, cnt) in enumerate(sorted_names)
    ])

    # 3. 指定路径阶段汇总（工作表3）
    df_target_phase = pd.DataFrame(target_phase_data)

    # 4. 高频节点路径分布（工作表4）- 修复：避免Excel 32767字符限制截断路径
    df_high_freq = pd.DataFrame([
        {
            "高频节点名称（出现≥10次）": name,
            "总出现次数": cnt,
            "涉及阶段总数": len(node_phase_map.get(name, set())),
            "main_quests阶段数": sum(1 for p in node_phase_map.get(name, set()) if 'main_quests' in p),
            "side_quests阶段数": sum(1 for p in node_phase_map.get(name, set()) if 'side_quests' in p),
            "minor_quests阶段数": sum(1 for p in node_phase_map.get(name, set()) if 'minor_quests' in p)
        }
        for name, cnt in sorted(name_counter.items()) if cnt >= 10
    ])

    # 5. 指定路径-高频节点次数矩阵（工作表5）
    matrix_data = []
    for phase in sorted(phase_node_counter.keys()):
        row = {"指定路径（main/side/minor quests）": phase}
        for node_name in high_freq_nodes:
            row[node_name] = phase_node_counter[phase].get(node_name, 0)
        matrix_data.append(row)
    df_matrix = pd.DataFrame(matrix_data)

    # 6. 所有阶段-节点类名次数矩阵（工作表6）
    class_matrix_data = []
    class_headers = []
    for node_class in sorted(all_node_classes):
        desc = NODE_CLASS_DESCRIPTION.get(node_class, "无描述")
        class_headers.append(f"{node_class}\n（{desc}）")  # 换行显示类名+描述

    for phase in sorted(all_phase_class_counter.keys()):
        row = {"所有阶段路径": phase}
        for idx, node_class in enumerate(sorted(all_node_classes)):
            row[class_headers[idx]] = all_phase_class_counter[phase].get(node_class, 0)
        class_matrix_data.append(row)
    df_class_matrix = pd.DataFrame(class_matrix_data)

    # 7. 节点类名-功能描述映射（工作表7）
    class_desc_data = []
    # 先添加有描述的类名
    for node_class in sorted(NODE_CLASS_DESCRIPTION.keys()):
        class_desc_data.append({
            "节点类名": node_class,
            "功能描述": NODE_CLASS_DESCRIPTION[node_class]
        })
    # 再添加读取到但无描述的类名
    for node_class in sorted(all_node_classes):
        if node_class not in NODE_CLASS_DESCRIPTION:
            class_desc_data.append({
                "节点类名": node_class,
                "功能描述": "无匹配描述"
            })
    df_class_desc = pd.DataFrame(class_desc_data)

    # 最终修复：仅一次保存Excel，包含所有7个工作表（之前重复保存导致覆盖）
    try:
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df_all_phase.to_excel(writer, sheet_name="所有阶段汇总", index=False)
            df_node_count.to_excel(writer, sheet_name="指定路径节点统计", index=False)
            df_target_phase.to_excel(writer, sheet_name="指定路径阶段汇总", index=False)
            df_high_freq.to_excel(writer, sheet_name="高频节点路径分布", index=False)
            df_matrix.to_excel(writer, sheet_name="指定路径-高频节点次数矩阵", index=False)
            df_class_matrix.to_excel(writer, sheet_name="所有阶段-节点类名次数矩阵", index=False)
            df_class_desc.to_excel(writer, sheet_name="节点类名-功能描述映射", index=False)
        print(f"✅ 成功生成7个工作表！文件保存至：{output_excel}")
    except Exception as e:
        print(f"❌ 保存Excel失败：{str(e)}")


if __name__ == "__main__":
    INPUT_JSON = ["quest_all_nodes.txt"]  # 确保文件路径正确
    OUTPUT_EXCEL = "quest_nodes_compact_v2.xlsx"
    json_to_compact_excel(INPUT_JSON, OUTPUT_EXCEL)