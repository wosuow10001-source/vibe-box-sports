"""
다국어 번역 모듈
지원 언어: 한국어, 영어, 일본어, 중국어(간체), 스페인어
"""

class Translator:
    """다국어 번역 클래스"""
    
    def __init__(self, language='ko'):
        """
        Args:
            language (str): 언어 코드 (ko, en, ja, zh, es)
        """
        self.language = language
        self.translations = self._load_translations()
    
    def _load_translations(self):
        """모든 번역 데이터 로드"""
        return {
            # 앱 제목 및 기본 정보
            'app_title': {
                'ko': '📡 VIBE BOX Sports MatchSignal',
                'en': '📡 VIBE BOX Sports MatchSignal',
                'ja': '📡 VIBE BOX Sports MatchSignal',
                'zh': '📡 VIBE BOX Sports MatchSignal',
                'es': '📡 VIBE BOX Sports MatchSignal'
            },
            'app_caption': {
                'ko': '실시간 스포츠 경기 예측 및 분석 플랫폼',
                'en': 'Real-time Sports Match Prediction & Analysis Platform',
                'ja': 'リアルタイムスポーツ試合予測・分析プラットフォーム',
                'zh': '实时体育比赛预测和分析平台',
                'es': 'Plataforma de Predicción y Análisis de Partidos Deportivos en Tiempo Real'
            },
            
            # 실시간 데이터 안내
            'realtime_data_notice': {
                'ko': '📡 **실시간 데이터 사용 중** - ESPN API를 통해 최신 선수 통계 및 경기 일정을 자동으로 가져옵니다.',
                'en': '📡 **Using Real-time Data** - Automatically fetching latest player stats and match schedules via ESPN API.',
                'ja': '📡 **リアルタイムデータ使用中** - ESPN APIを通じて最新の選手統計と試合スケジュールを自動取得します。',
                'zh': '📡 **使用实时数据** - 通过ESPN API自动获取最新球员统计和比赛日程。',
                'es': '📡 **Usando Datos en Tiempo Real** - Obteniendo automáticamente las últimas estadísticas de jugadores y calendarios de partidos a través de ESPN API.'
            },
            'info_button': {
                'ko': 'ℹ️ 정보',
                'en': 'ℹ️ Info',
                'ja': 'ℹ️ 情報',
                'zh': 'ℹ️ 信息',
                'es': 'ℹ️ Información'
            },
            
            # 사이드바
            'refresh_data': {
                'ko': '🔄 데이터 새로고침',
                'en': '🔄 Refresh Data',
                'ja': '🔄 データ更新',
                'zh': '🔄 刷新数据',
                'es': '🔄 Actualizar Datos'
            },
            'sport': {
                'ko': '스포츠 종목',
                'en': 'Sport',
                'ja': 'スポーツ種目',
                'zh': '体育项目',
                'es': 'Deporte'
            },
            'league': {
                'ko': '리그',
                'en': 'League',
                'ja': 'リーグ',
                'zh': '联赛',
                'es': 'Liga'
            },
            'language': {
                'ko': '언어',
                'en': 'Language',
                'ja': '言語',
                'zh': '语言',
                'es': 'Idioma'
            },
            
            # 스포츠 종목
            'soccer': {
                'ko': '축구',
                'en': 'Soccer',
                'ja': 'サッカー',
                'zh': '足球',
                'es': 'Fútbol'
            },
            'baseball': {
                'ko': '야구',
                'en': 'Baseball',
                'ja': '野球',
                'zh': '棒球',
                'es': 'Béisbol'
            },
            'basketball': {
                'ko': '농구',
                'en': 'Basketball',
                'ja': 'バスケットボール',
                'zh': '篮球',
                'es': 'Baloncesto'
            },
            'volleyball': {
                'ko': '배구',
                'en': 'Volleyball',
                'ja': 'バレーボール',
                'zh': '排球',
                'es': 'Voleibol'
            },
            
            # 탭 이름
            'tab_match_prediction': {
                'ko': '📊 경기 예측',
                'en': '📊 Match Prediction',
                'ja': '📊 試合予測',
                'zh': '📊 比赛预测',
                'es': '📊 Predicción de Partido'
            },
            'tab_team_analysis': {
                'ko': '📈 팀 분석',
                'en': '📈 Team Analysis',
                'ja': '📈 チーム分析',
                'zh': '📈 球队分析',
                'es': '📈 Análisis de Equipo'
            },
            'tab_player_analysis': {
                'ko': '👤 선수 분석',
                'en': '👤 Player Analysis',
                'ja': '👤 選手分析',
                'zh': '👤 球员分析',
                'es': '👤 Análisis de Jugador'
            },
            'tab_schedule': {
                'ko': '📅 경기 일정',
                'en': '📅 Match Schedule',
                'ja': '📅 試合スケジュール',
                'zh': '📅 比赛日程',
                'es': '📅 Calendario de Partidos'
            },
            'tab_injury_report': {
                'ko': '🏥 부상 리포트',
                'en': '🏥 Injury Report',
                'ja': '🏥 怪我レポート',
                'zh': '🏥 伤病报告',
                'es': '🏥 Informe de Lesiones'
            },
            'tab_coaching_staff': {
                'ko': '👔 코칭스태프',
                'en': '👔 Coaching Staff',
                'ja': '👔 コーチングスタッフ',
                'zh': '👔 教练组',
                'es': '👔 Cuerpo Técnico'
            },
            'tab_settings': {
                'ko': '⚙️ 설정',
                'en': '⚙️ Settings',
                'ja': '⚙️ 設定',
                'zh': '⚙️ 设置',
                'es': '⚙️ Configuración'
            },
            
            # 경기 예측
            'home_team': {
                'ko': '홈 팀',
                'en': 'Home Team',
                'ja': 'ホームチーム',
                'zh': '主队',
                'es': 'Equipo Local'
            },
            'away_team': {
                'ko': '원정 팀',
                'en': 'Away Team',
                'ja': 'アウェイチーム',
                'zh': '客队',
                'es': 'Equipo Visitante'
            },
            'team_select': {
                'ko': '팀 선택',
                'en': 'Select Team',
                'ja': 'チーム選択',
                'zh': '选择球队',
                'es': 'Seleccionar Equipo'
            },
            'recent_winrate': {
                'ko': '최근 5경기 승률',
                'en': 'Recent 5 Games Win Rate',
                'ja': '最近5試合勝率',
                'zh': '最近5场胜率',
                'es': 'Tasa de Victoria Últimos 5 Partidos'
            },
            'home_winrate': {
                'ko': '홈 경기 승률',
                'en': 'Home Win Rate',
                'ja': 'ホーム勝率',
                'zh': '主场胜率',
                'es': 'Tasa de Victoria en Casa'
            },
            'away_winrate': {
                'ko': '원정 경기 승률',
                'en': 'Away Win Rate',
                'ja': 'アウェイ勝率',
                'zh': '客场胜率',
                'es': 'Tasa de Victoria Fuera'
            },
            'avg_goals': {
                'ko': '평균 득점',
                'en': 'Average Goals',
                'ja': '平均得点',
                'zh': '平均进球',
                'es': 'Goles Promedio'
            },
            'league_rank': {
                'ko': '리그 순위',
                'en': 'League Rank',
                'ja': 'リーグ順位',
                'zh': '联赛排名',
                'es': 'Posición en Liga'
            },
            'points': {
                'ko': '승점',
                'en': 'Points',
                'ja': 'ポイント',
                'zh': '积分',
                'es': 'Puntos'
            },
            
            # 경기 조건
            'match_conditions': {
                'ko': '경기 조건',
                'en': 'Match Conditions',
                'ja': '試合条件',
                'zh': '比赛条件',
                'es': 'Condiciones del Partido'
            },
            'weather': {
                'ko': '날씨',
                'en': 'Weather',
                'ja': '天気',
                'zh': '天气',
                'es': 'Clima'
            },
            'temperature': {
                'ko': '기온 (°C)',
                'en': 'Temperature (°C)',
                'ja': '気温 (°C)',
                'zh': '温度 (°C)',
                'es': 'Temperatura (°C)'
            },
            'field_condition': {
                'ko': '경기장 상태',
                'en': 'Field Condition',
                'ja': 'フィールド状態',
                'zh': '场地状况',
                'es': 'Condición del Campo'
            },
            'match_importance': {
                'ko': '경기 중요도',
                'en': 'Match Importance',
                'ja': '試合重要度',
                'zh': '比赛重要性',
                'es': 'Importancia del Partido'
            },
            'rest_days': {
                'ko': '휴식일',
                'en': 'Rest Days',
                'ja': '休息日',
                'zh': '休息天数',
                'es': 'Días de Descanso'
            },
            
            # 날씨 옵션
            'sunny': {
                'ko': '맑음',
                'en': 'Sunny',
                'ja': '晴れ',
                'zh': '晴天',
                'es': 'Soleado'
            },
            'cloudy': {
                'ko': '흐림',
                'en': 'Cloudy',
                'ja': '曇り',
                'zh': '多云',
                'es': 'Nublado'
            },
            'rainy': {
                'ko': '비',
                'en': 'Rainy',
                'ja': '雨',
                'zh': '雨天',
                'es': 'Lluvioso'
            },
            'snowy': {
                'ko': '눈',
                'en': 'Snowy',
                'ja': '雪',
                'zh': '下雪',
                'es': 'Nevado'
            },
            'windy': {
                'ko': '강풍',
                'en': 'Windy',
                'ja': '強風',
                'zh': '大风',
                'es': 'Ventoso'
            },
            
            # 경기장 상태
            'excellent': {
                'ko': '최상',
                'en': 'Excellent',
                'ja': '最高',
                'zh': '优秀',
                'es': 'Excelente'
            },
            'good': {
                'ko': '양호',
                'en': 'Good',
                'ja': '良好',
                'zh': '良好',
                'es': 'Bueno'
            },
            'average': {
                'ko': '보통',
                'en': 'Average',
                'ja': '普通',
                'zh': '一般',
                'es': 'Regular'
            },
            'poor': {
                'ko': '불량',
                'en': 'Poor',
                'ja': '悪い',
                'zh': '差',
                'es': 'Malo'
            },
            
            # 경기 중요도
            'normal': {
                'ko': '일반',
                'en': 'Normal',
                'ja': '通常',
                'zh': '普通',
                'es': 'Normal'
            },
            'important': {
                'ko': '중요',
                'en': 'Important',
                'ja': '重要',
                'zh': '重要',
                'es': 'Importante'
            },
            'very_important': {
                'ko': '매우중요',
                'en': 'Very Important',
                'ja': '非常に重要',
                'zh': '非常重要',
                'es': 'Muy Importante'
            },
            
            # 예측 버튼 및 결과
            'run_prediction': {
                'ko': '🎯 예측 실행',
                'en': '🎯 Run Prediction',
                'ja': '🎯 予測実行',
                'zh': '🎯 运行预测',
                'es': '🎯 Ejecutar Predicción'
            },
            'prediction_complete': {
                'ko': '예측 완료!',
                'en': 'Prediction Complete!',
                'ja': '予測完了！',
                'zh': '预测完成！',
                'es': '¡Predicción Completa!'
            },
            'home_win_prob': {
                'ko': '홈 승리 확률',
                'en': 'Home Win Probability',
                'ja': 'ホーム勝利確率',
                'zh': '主队获胜概率',
                'es': 'Probabilidad de Victoria Local'
            },
            'draw_prob': {
                'ko': '무승부 확률',
                'en': 'Draw Probability',
                'ja': '引き分け確率',
                'zh': '平局概率',
                'es': 'Probabilidad de Empate'
            },
            'away_win_prob': {
                'ko': '원정 승리 확률',
                'en': 'Away Win Probability',
                'ja': 'アウェイ勝利確率',
                'zh': '客队获胜概率',
                'es': 'Probabilidad de Victoria Visitante'
            },
            'expected_score': {
                'ko': '예상 스코어',
                'en': 'Expected Score',
                'ja': '予想スコア',
                'zh': '预期比分',
                'es': 'Puntuación Esperada'
            },
            'confidence': {
                'ko': '신뢰도',
                'en': 'Confidence',
                'ja': '信頼度',
                'zh': '置信度',
                'es': 'Confianza'
            },
            
            # 부상 정보
            'injury_info': {
                'ko': '⚕️ 부상 선수 정보가 예측에 반영되었습니다.',
                'en': '⚕️ Injury information has been reflected in the prediction.',
                'ja': '⚕️ 怪我情報が予測に反映されました。',
                'zh': '⚕️ 伤病信息已反映在预测中。',
                'es': '⚕️ La información de lesiones se ha reflejado en la predicción.'
            },
            'injured_players': {
                'ko': '부상자',
                'en': 'Injured',
                'ja': '負傷者',
                'zh': '伤员',
                'es': 'Lesionados'
            },
            
            # 부상 상태
            'out': {
                'ko': '결장',
                'en': 'Out',
                'ja': '欠場',
                'zh': '缺阵',
                'es': 'Fuera'
            },
            'day_to_day': {
                'ko': '일일 점검',
                'en': 'Day-to-Day',
                'ja': '日々確認',
                'zh': '每日观察',
                'es': 'Día a Día'
            },
            'questionable': {
                'ko': '출전 불투명',
                'en': 'Questionable',
                'ja': '出場不透明',
                'zh': '出场存疑',
                'es': 'Dudoso'
            },
            'doubtful': {
                'ko': '출전 가능성 낮음',
                'en': 'Doubtful',
                'ja': '出場可能性低',
                'zh': '出场可能性低',
                'es': 'Improbable'
            },
            
            # 선수 분석
            'player_analysis': {
                'ko': '선수 개별 분석',
                'en': 'Individual Player Analysis',
                'ja': '選手個別分析',
                'zh': '球员个人分析',
                'es': 'Análisis Individual de Jugador'
            },
            'select_player': {
                'ko': '선수 선택',
                'en': 'Select Player',
                'ja': '選手選択',
                'zh': '选择球员',
                'es': 'Seleccionar Jugador'
            },
            'run_analysis': {
                'ko': '분석 실행',
                'en': 'Run Analysis',
                'ja': '分析実行',
                'zh': '运行分析',
                'es': 'Ejecutar Análisis'
            },
            'refresh_roster': {
                'ko': '🔄 로스터 새로고침',
                'en': '🔄 Refresh Roster',
                'ja': '🔄 ロスター更新',
                'zh': '🔄 刷新名单',
                'es': '🔄 Actualizar Plantilla'
            },
            
            # 통계
            'age': {
                'ko': '나이',
                'en': 'Age',
                'ja': '年齢',
                'zh': '年龄',
                'es': 'Edad'
            },
            'position': {
                'ko': '포지션',
                'en': 'Position',
                'ja': 'ポジション',
                'zh': '位置',
                'es': 'Posición'
            },
            'matches_played': {
                'ko': '출전 경기',
                'en': 'Matches Played',
                'ja': '出場試合',
                'zh': '出场比赛',
                'es': 'Partidos Jugados'
            },
            'goals': {
                'ko': '골',
                'en': 'Goals',
                'ja': 'ゴール',
                'zh': '进球',
                'es': 'Goles'
            },
            'assists': {
                'ko': '어시스트',
                'en': 'Assists',
                'ja': 'アシスト',
                'zh': '助攻',
                'es': 'Asistencias'
            },
            'rating': {
                'ko': '평균 평점',
                'en': 'Average Rating',
                'ja': '平均評価',
                'zh': '平均评分',
                'es': 'Calificación Promedio'
            },
            'condition': {
                'ko': '컨디션',
                'en': 'Condition',
                'ja': 'コンディション',
                'zh': '状态',
                'es': 'Condición'
            },
            'injury_status': {
                'ko': '부상 상태',
                'en': 'Injury Status',
                'ja': '怪我状態',
                'zh': '伤病状态',
                'es': 'Estado de Lesión'
            },
            'fatigue': {
                'ko': '피로도',
                'en': 'Fatigue',
                'ja': '疲労度',
                'zh': '疲劳度',
                'es': 'Fatiga'
            },
            
            # 메시지
            'loading': {
                'ko': '데이터 분석 중...',
                'en': 'Analyzing data...',
                'ja': 'データ分析中...',
                'zh': '数据分析中...',
                'es': 'Analizando datos...'
            },
            'cache_cleared': {
                'ko': '✅ 실시간 데이터 캐시 초기화 완료!',
                'en': '✅ Real-time data cache cleared!',
                'ja': '✅ リアルタイムデータキャッシュクリア完了！',
                'zh': '✅ 实时数据缓存已清除！',
                'es': '✅ ¡Caché de datos en tiempo real borrado!'
            },
            'language_header': {
                'ko': '🌍 언어 / Language',
                'en': '🌍 Language',
                'ja': '🌍 言語',
                'zh': '🌍 语言',
                'es': '🌍 Idioma'
            },
            'select_language': {
                'ko': '언어 선택 / Select Language',
                'en': 'Select Language',
                'ja': '言語選択',
                'zh': '选择语言',
                'es': 'Seleccionar Idioma'
            },
            'season_data_info': {
                'ko': '⚡ 2025-26 시즌 실제 데이터 (2026년 3월 16일 기준)',
                'en': '⚡ 2025-26 Season Real Data (as of March 16, 2026)',
                'ja': '⚡ 2025-26シーズン実データ（2026年3月16日時点）',
                'zh': '⚡ 2025-26赛季真实数据（截至2026年3月16日）',
                'es': '⚡ Datos Reales Temporada 2025-26 (al 16 de marzo de 2026)'
            },
            'ad_space': {
                'ko': '광고 공간',
                'en': 'Ad Space',
                'ja': '広告スペース',
                'zh': '广告位',
                'es': 'Espacio Publicitario'
            },
            'sponsor_message': {
                'ko': '스폰서 및 광고 문의',
                'en': 'Sponsor & Ad Inquiries',
                'ja': 'スポンサー・広告お問い合わせ',
                'zh': '赞助商和广告咨询',
                'es': 'Consultas de Patrocinio y Publicidad'
            },
            'conference_filter': {
                'ko': '컨퍼런스 필터',
                'en': 'Conference Filter',
                'ja': 'カンファレンスフィルター',
                'zh': '联盟筛选',
                'es': 'Filtro de Conferencia'
            },
            'all': {
                'ko': '전체',
                'en': 'All',
                'ja': '全体',
                'zh': '全部',
                'es': 'Todos'
            },
            'realtime_data_sources': {
                'ko': '**실시간 데이터 소스:**\n- 선수 통계: ESPN API\n- 경기 일정: ESPN API\n- 업데이트: 1시간마다 자동\n- 캐시: 사이드바 \'데이터 새로고침\' 버튼으로 수동 갱신 가능',
                'en': '**Real-time Data Sources:**\n- Player Stats: ESPN API\n- Match Schedule: ESPN API\n- Updates: Automatic every hour\n- Cache: Manual refresh via sidebar \'Refresh Data\' button',
                'ja': '**リアルタイムデータソース:**\n- 選手統計: ESPN API\n- 試合スケジュール: ESPN API\n- 更新: 1時間ごとに自動\n- キャッシュ: サイドバー「データ更新」ボタンで手動更新可能',
                'zh': '**实时数据源:**\n- 球员统计: ESPN API\n- 比赛日程: ESPN API\n- 更新: 每小时自动\n- 缓存: 通过侧边栏"刷新数据"按钮手动刷新',
                'es': '**Fuentes de Datos en Tiempo Real:**\n- Estadísticas de Jugadores: ESPN API\n- Calendario de Partidos: ESPN API\n- Actualizaciones: Automáticas cada hora\n- Caché: Actualización manual mediante el botón \'Actualizar Datos\' en la barra lateral'
            },
            
            # 탭 메뉴
            'tab_match_prediction': {
                'ko': '📊 경기 예측',
                'en': '📊 Match Prediction',
                'ja': '📊 試合予測',
                'zh': '📊 比赛预测',
                'es': '📊 Predicción de Partido'
            },
            'tab_team_analysis': {
                'ko': '📈 팀 분석',
                'en': '📈 Team Analysis',
                'ja': '📈 チーム分析',
                'zh': '📈 球队分析',
                'es': '📈 Análisis de Equipo'
            },
            'tab_player_analysis': {
                'ko': '👤 선수 분석',
                'en': '👤 Player Analysis',
                'ja': '👤 選手分析',
                'zh': '👤 球员分析',
                'es': '👤 Análisis de Jugador'
            },
            'tab_schedule': {
                'ko': '📅 경기 일정',
                'en': '📅 Match Schedule',
                'ja': '📅 試合スケジュール',
                'zh': '📅 比赛日程',
                'es': '📅 Calendario de Partidos'
            },
            'tab_injury_report': {
                'ko': '🏥 부상 리포트',
                'en': '🏥 Injury Report',
                'ja': '🏥 怪我レポート',
                'zh': '🏥 伤病报告',
                'es': '🏥 Informe de Lesiones'
            },
            'tab_coaching_staff': {
                'ko': '👔 코칭스태프',
                'en': '👔 Coaching Staff',
                'ja': '👔 コーチングスタッフ',
                'zh': '👔 教练组',
                'es': '👔 Cuerpo Técnico'
            },
            'tab_settings': {
                'ko': '⚙️ 설정',
                'en': '⚙️ Settings',
                'ja': '⚙️ 設定',
                'zh': '⚙️ 设置',
                'es': '⚙️ Configuración'
            },
            
            # 경기 예측 탭
            'match_prediction': {
                'ko': '경기 예측',
                'en': 'Match Prediction',
                'ja': '試合予測',
                'zh': '比赛预测',
                'es': 'Predicción de Partido'
            },
            'home_team': {
                'ko': '홈 팀',
                'en': 'Home Team',
                'ja': 'ホームチーム',
                'zh': '主队',
                'es': 'Equipo Local'
            },
            'away_team': {
                'ko': '원정 팀',
                'en': 'Away Team',
                'ja': 'アウェイチーム',
                'zh': '客队',
                'es': 'Equipo Visitante'
            },
            'select_team': {
                'ko': '팀 선택',
                'en': 'Select Team',
                'ja': 'チーム選択',
                'zh': '选择球队',
                'es': 'Seleccionar Equipo'
            },
            'league_rank': {
                'ko': '리그 순위',
                'en': 'League Rank',
                'ja': 'リーグ順位',
                'zh': '联赛排名',
                'es': 'Posición en Liga'
            },
            'points': {
                'ko': '승점',
                'en': 'Points',
                'ja': 'ポイント',
                'zh': '积分',
                'es': 'Puntos'
            },
            'recent_5_winrate': {
                'ko': '최근 5경기 승률',
                'en': 'Recent 5 Games Win Rate',
                'ja': '最近5試合勝率',
                'zh': '最近5场胜率',
                'es': 'Tasa de Victoria Últimos 5 Partidos'
            },
            'home_winrate': {
                'ko': '홈 경기 승률',
                'en': 'Home Win Rate',
                'ja': 'ホーム勝率',
                'zh': '主场胜率',
                'es': 'Tasa de Victoria Local'
            },
            'away_winrate': {
                'ko': '원정 경기 승률',
                'en': 'Away Win Rate',
                'ja': 'アウェイ勝率',
                'zh': '客场胜率',
                'es': 'Tasa de Victoria Visitante'
            },
            'avg_score': {
                'ko': '평균 득점',
                'en': 'Average Score',
                'ja': '平均得点',
                'zh': '平均得分',
                'es': 'Puntuación Promedio'
            },
            'match_conditions': {
                'ko': '경기 조건',
                'en': 'Match Conditions',
                'ja': '試合条件',
                'zh': '比赛条件',
                'es': 'Condiciones del Partido'
            },
            'weather': {
                'ko': '날씨',
                'en': 'Weather',
                'ja': '天気',
                'zh': '天气',
                'es': 'Clima'
            },
            'weather_sunny': {
                'ko': '맑음',
                'en': 'Sunny',
                'ja': '晴れ',
                'zh': '晴天',
                'es': 'Soleado'
            },
            'weather_cloudy': {
                'ko': '흐림',
                'en': 'Cloudy',
                'ja': '曇り',
                'zh': '多云',
                'es': 'Nublado'
            },
            'weather_rain': {
                'ko': '비',
                'en': 'Rain',
                'ja': '雨',
                'zh': '雨',
                'es': 'Lluvia'
            },
            'weather_snow': {
                'ko': '눈',
                'en': 'Snow',
                'ja': '雪',
                'zh': '雪',
                'es': 'Nieve'
            },
            'weather_windy': {
                'ko': '강풍',
                'en': 'Windy',
                'ja': '強風',
                'zh': '大风',
                'es': 'Ventoso'
            },
            'temperature': {
                'ko': '기온 (°C)',
                'en': 'Temperature (°C)',
                'ja': '気温 (°C)',
                'zh': '温度 (°C)',
                'es': 'Temperatura (°C)'
            },
            'field_condition': {
                'ko': '경기장 상태',
                'en': 'Field Condition',
                'ja': 'フィールド状態',
                'zh': '场地状况',
                'es': 'Condición del Campo'
            },
            'field_excellent': {
                'ko': '최상',
                'en': 'Excellent',
                'ja': '最高',
                'zh': '最佳',
                'es': 'Excelente'
            },
            'field_good': {
                'ko': '양호',
                'en': 'Good',
                'ja': '良好',
                'zh': '良好',
                'es': 'Bueno'
            },
            'field_fair': {
                'ko': '보통',
                'en': 'Fair',
                'ja': '普通',
                'zh': '一般',
                'es': 'Regular'
            },
            'field_poor': {
                'ko': '불량',
                'en': 'Poor',
                'ja': '不良',
                'zh': '较差',
                'es': 'Malo'
            },
            'match_importance': {
                'ko': '경기 중요도',
                'en': 'Match Importance',
                'ja': '試合重要度',
                'zh': '比赛重要性',
                'es': 'Importancia del Partido'
            },
            'importance_normal': {
                'ko': '일반',
                'en': 'Normal',
                'ja': '通常',
                'zh': '普通',
                'es': 'Normal'
            },
            'importance_important': {
                'ko': '중요',
                'en': 'Important',
                'ja': '重要',
                'zh': '重要',
                'es': 'Importante'
            },
            'importance_very_important': {
                'ko': '매우중요',
                'en': 'Very Important',
                'ja': '非常に重要',
                'zh': '非常重要',
                'es': 'Muy Importante'
            },
            'rest_days_home': {
                'ko': '홈팀 휴식일',
                'en': 'Home Team Rest Days',
                'ja': 'ホームチーム休息日',
                'zh': '主队休息日',
                'es': 'Días de Descanso Equipo Local'
            },
            'rest_days_away': {
                'ko': '원정팀 휴식일',
                'en': 'Away Team Rest Days',
                'ja': 'アウェイチーム休息日',
                'zh': '客队休息日',
                'es': 'Días de Descanso Equipo Visitante'
            },
            'run_prediction': {
                'ko': '🎯 예측 실행',
                'en': '🎯 Run Prediction',
                'ja': '🎯 予測実行',
                'zh': '🎯 运行预测',
                'es': '🎯 Ejecutar Predicción'
            },
            'analyzing_data': {
                'ko': '데이터 분석 중...',
                'en': 'Analyzing data...',
                'ja': 'データ分析中...',
                'zh': '数据分析中...',
                'es': 'Analizando datos...'
            },
            'rank_suffix': {
                'ko': '위',
                'en': '',
                'ja': '位',
                'zh': '名',
                'es': 'º'
            },
            'points_suffix': {
                'ko': '점',
                'en': ' pts',
                'ja': 'ポイント',
                'zh': '分',
                'es': ' pts'
            },
            
            # 예측 결과
            'prediction_complete': {
                'ko': '예측 완료!',
                'en': 'Prediction Complete!',
                'ja': '予測完了！',
                'zh': '预测完成！',
                'es': '¡Predicción Completa!'
            },
            'home_win_prob': {
                'ko': '홈 승리 확률',
                'en': 'Home Win Probability',
                'ja': 'ホーム勝利確率',
                'zh': '主队获胜概率',
                'es': 'Probabilidad de Victoria Local'
            },
            'draw_prob': {
                'ko': '무승부 확률',
                'en': 'Draw Probability',
                'ja': '引き分け確率',
                'zh': '平局概率',
                'es': 'Probabilidad de Empate'
            },
            'away_win_prob': {
                'ko': '원정 승리 확률',
                'en': 'Away Win Probability',
                'ja': 'アウェイ勝利確率',
                'zh': '客队获胜概率',
                'es': 'Probabilidad de Victoria Visitante'
            },
            'detailed_analysis': {
                'ko': '📋 상세 분석',
                'en': '📋 Detailed Analysis',
                'ja': '📋 詳細分析',
                'zh': '📋 详细分析',
                'es': '📋 Análisis Detallado'
            },
            'key_factors': {
                'ko': '**주요 영향 요인**',
                'en': '**Key Factors**',
                'ja': '**主要影響要因**',
                'zh': '**主要影响因素**',
                'es': '**Factores Clave**'
            },
            'prediction_confidence': {
                'ko': '**예측 신뢰도**',
                'en': '**Prediction Confidence**',
                'ja': '**予測信頼度**',
                'zh': '**预测置信度**',
                'es': '**Confianza de Predicción**'
            },
            'confidence_label': {
                'ko': '신뢰도: ',
                'en': 'Confidence: ',
                'ja': '信頼度: ',
                'zh': '置信度: ',
                'es': 'Confianza: '
            },
            
            # 팀 분석 탭
            'team_analysis_title': {
                'ko': '팀 심층 분석',
                'en': 'Team In-Depth Analysis',
                'ja': 'チーム詳細分析',
                'zh': '球队深度分析',
                'es': 'Análisis Profundo del Equipo'
            },
            'select_team_analysis': {
                'ko': '분석할 팀',
                'en': 'Team to Analyze',
                'ja': '分析するチーム',
                'zh': '要分析的球队',
                'es': 'Equipo a Analizar'
            },
            'run_team_analysis': {
                'ko': '팀 분석 실행',
                'en': 'Run Team Analysis',
                'ja': 'チーム分析実行',
                'zh': '运行球队分析',
                'es': 'Ejecutar Análisis de Equipo'
            },
            'coaching_staff': {
                'ko': '👔 코칭스태프',
                'en': '👔 Coaching Staff',
                'ja': '👔 コーチングスタッフ',
                'zh': '👔 教练组',
                'es': '👔 Cuerpo Técnico'
            },
            'head_coach_label': {
                'ko': '**감독:**',
                'en': '**Head Coach:**',
                'ja': '**監督:**',
                'zh': '**主教练:**',
                'es': '**Entrenador Principal:**'
            },
            'coaches_label': {
                'ko': '**코치진:**',
                'en': '**Coaches:**',
                'ja': '**コーチ陣:**',
                'zh': '**教练组:**',
                'es': '**Cuerpo Técnico:**'
            },
            'people_count': {
                'ko': '명',
                'en': '',
                'ja': '名',
                'zh': '人',
                'es': ''
            },
            'coach_details': {
                'ko': '코치진 상세 정보',
                'en': 'Coach Details',
                'ja': 'コーチ詳細情報',
                'zh': '教练详细信息',
                'es': 'Detalles del Cuerpo Técnico'
            },
            'recent_form': {
                'ko': '📊 최근 경기 폼',
                'en': '📊 Recent Form',
                'ja': '📊 最近の試合フォーム',
                'zh': '📊 最近比赛状态',
                'es': '📊 Forma Reciente'
            },
            'strengths': {
                'ko': '💪 강점',
                'en': '💪 Strengths',
                'ja': '💪 強み',
                'zh': '💪 优势',
                'es': '💪 Fortalezas'
            },
            'weaknesses': {
                'ko': '⚠️ 약점',
                'en': '⚠️ Weaknesses',
                'ja': '⚠️ 弱点',
                'zh': '⚠️ 弱点',
                'es': '⚠️ Debilidades'
            },
            
            # 선수 분석 탭
            'player_individual_analysis': {
                'ko': '선수 개별 분석',
                'en': 'Individual Player Analysis',
                'ja': '選手個別分析',
                'zh': '球员个人分析',
                'es': 'Análisis Individual de Jugador'
            },
            'refresh_roster': {
                'ko': '🔄 로스터 새로고침',
                'en': '🔄 Refresh Roster',
                'ja': '🔄 ロスター更新',
                'zh': '🔄 刷新名单',
                'es': '🔄 Actualizar Plantilla'
            },
            'select_player': {
                'ko': '선수 선택',
                'en': 'Select Player',
                'ja': '選手選択',
                'zh': '选择球员',
                'es': 'Seleccionar Jugador'
            },
            'run_player_analysis': {
                'ko': '선수 분석 실행',
                'en': 'Run Player Analysis',
                'ja': '選手分析実行',
                'zh': '运行球员分析',
                'es': 'Ejecutar Análisis de Jugador'
            },
            'age': {
                'ko': '나이',
                'en': 'Age',
                'ja': '年齢',
                'zh': '年龄',
                'es': 'Edad'
            },
            'age_suffix': {
                'ko': '세',
                'en': ' years',
                'ja': '歳',
                'zh': '岁',
                'es': ' años'
            },
            'matches_played': {
                'ko': '출전 경기',
                'en': 'Matches Played',
                'ja': '出場試合',
                'zh': '出场比赛',
                'es': 'Partidos Jugados'
            },
            'avg_points': {
                'ko': '평균 득점',
                'en': 'Average Points',
                'ja': '平均得点',
                'zh': '平均得分',
                'es': 'Puntos Promedio'
            },
            'avg_rebounds': {
                'ko': '평균 리바운드',
                'en': 'Average Rebounds',
                'ja': '平均リバウンド',
                'zh': '平均篮板',
                'es': 'Rebotes Promedio'
            },
            'goals': {
                'ko': '골',
                'en': 'Goals',
                'ja': 'ゴール',
                'zh': '进球',
                'es': 'Goles'
            },
            'assists': {
                'ko': '어시스트',
                'en': 'Assists',
                'ja': 'アシスト',
                'zh': '助攻',
                'es': 'Asistencias'
            },
            'avg_rating': {
                'ko': '평균 평점',
                'en': 'Average Rating',
                'ja': '平均評価',
                'zh': '平均评分',
                'es': 'Calificación Promedio'
            },
            'condition': {
                'ko': '컨디션',
                'en': 'Condition',
                'ja': 'コンディション',
                'zh': '状态',
                'es': 'Condición'
            },
            'injury_status': {
                'ko': '부상 상태',
                'en': 'Injury Status',
                'ja': '怪我状態',
                'zh': '伤病状态',
                'es': 'Estado de Lesión'
            },
            'roster_cache_cleared': {
                'ko': '✅ 로스터 캐시 초기화 완료!',
                'en': '✅ Roster cache cleared!',
                'ja': '✅ ロスターキャッシュクリア完了！',
                'zh': '✅ 名单缓存已清除！',
                'es': '✅ ¡Caché de plantilla borrado!'
            },
            'real_data': {
                'ko': '✅ 실제 2025-26 시즌 데이터',
                'en': '✅ Real 2025-26 Season Data',
                'ja': '✅ 実際の2025-26シーズンデータ',
                'zh': '✅ 真实2025-26赛季数据',
                'es': '✅ Datos Reales Temporada 2025-26'
            },
            'simulated_data': {
                'ko': '⚠️ 시뮬레이션 데이터',
                'en': '⚠️ Simulated Data',
                'ja': '⚠️ シミュレーションデータ',
                'zh': '⚠️ 模拟数据',
                'es': '⚠️ Datos Simulados'
            },
            
            # 팀 분석 관련
            'team_analysis_title': {
                'ko': '팀 심층 분석',
                'en': 'Team In-Depth Analysis',
                'ja': 'チーム詳細分析',
                'zh': '球队深度分析',
                'es': 'Análisis Profundo del Equipo'
            },
            'select_team': {
                'ko': '분석할 팀',
                'en': 'Team to Analyze',
                'ja': '分析するチーム',
                'zh': '分析球队',
                'es': 'Equipo a Analizar'
            },
            'run_team_analysis': {
                'ko': '팀 분석 실행',
                'en': 'Run Team Analysis',
                'ja': 'チーム分析実行',
                'zh': '运行球队分析',
                'es': 'Ejecutar Análisis de Equipo'
            },
            'recent_form': {
                'ko': '최근 경기 폼',
                'en': 'Recent Form',
                'ja': '最近の試合フォーム',
                'zh': '最近比赛状态',
                'es': 'Forma Reciente'
            },
            'strengths': {
                'ko': '강점',
                'en': 'Strengths',
                'ja': '強み',
                'zh': '优势',
                'es': 'Fortalezas'
            },
            'weaknesses': {
                'ko': '약점',
                'en': 'Weaknesses',
                'ja': '弱点',
                'zh': '弱点',
                'es': 'Debilidades'
            },
            'head_coach': {
                'ko': '감독',
                'en': 'Head Coach',
                'ja': '監督',
                'zh': '主教练',
                'es': 'Entrenador Principal'
            },
            'coaching_staff_count': {
                'ko': '코치진',
                'en': 'Coaching Staff',
                'ja': 'コーチ陣',
                'zh': '教练组',
                'es': 'Cuerpo Técnico'
            },
            'coaching_details': {
                'ko': '코치진 상세 정보',
                'en': 'Coaching Staff Details',
                'ja': 'コーチ陣詳細情報',
                'zh': '教练组详细信息',
                'es': 'Detalles del Cuerpo Técnico'
            },
            
            # 경기 일정 관련
            'schedule_title': {
                'ko': '경기 일정',
                'en': 'Match Schedule',
                'ja': '試合スケジュール',
                'zh': '比赛日程',
                'es': 'Calendario de Partidos'
            },
            'schedule_mode': {
                'ko': '일정 보기 모드',
                'en': 'Schedule View Mode',
                'ja': 'スケジュール表示モード',
                'zh': '日程查看模式',
                'es': 'Modo de Vista de Calendario'
            },
            'all_schedules': {
                'ko': '전체 일정',
                'en': 'All Schedules',
                'ja': '全スケジュール',
                'zh': '全部日程',
                'es': 'Todos los Calendarios'
            },
            'league_schedule': {
                'ko': '리그별 일정',
                'en': 'League Schedule',
                'ja': 'リーグ別スケジュール',
                'zh': '联赛日程',
                'es': 'Calendario de Liga'
            },
            'team_schedule': {
                'ko': '팀별 일정',
                'en': 'Team Schedule',
                'ja': 'チーム別スケジュール',
                'zh': '球队日程',
                'es': 'Calendario de Equipo'
            },
            'all_leagues_upcoming': {
                'ko': '모든 리그 다가오는 경기',
                'en': 'All Leagues Upcoming Matches',
                'ja': '全リーグ今後の試合',
                'zh': '所有联赛即将比赛',
                'es': 'Próximos Partidos de Todas las Ligas'
            },
            'upcoming_matches': {
                'ko': '다가오는 경기',
                'en': 'Upcoming Matches',
                'ja': '今後の試合',
                'zh': '即将比赛',
                'es': 'Próximos Partidos'
            },
            'next_matches': {
                'ko': '다음 경기',
                'en': 'Next Matches',
                'ja': '次の試合',
                'zh': '下一场比赛',
                'es': 'Próximos Partidos'
            },
            'match_date': {
                'ko': '날짜',
                'en': 'Date',
                'ja': '日付',
                'zh': '日期',
                'es': 'Fecha'
            },
            'match_time': {
                'ko': '시간',
                'en': 'Time',
                'ja': '時間',
                'zh': '时间',
                'es': 'Hora'
            },
            'venue': {
                'ko': '장소',
                'en': 'Venue',
                'ja': '会場',
                'zh': '场地',
                'es': 'Estadio'
            },
            'tv_broadcast': {
                'ko': '중계',
                'en': 'TV Broadcast',
                'ja': '放送',
                'zh': '转播',
                'es': 'Transmisión TV'
            },
            'home_match': {
                'ko': '홈 경기',
                'en': 'Home Match',
                'ja': 'ホーム試合',
                'zh': '主场比赛',
                'es': 'Partido en Casa'
            },
            'away_match': {
                'ko': '원정 경기',
                'en': 'Away Match',
                'ja': 'アウェイ試合',
                'zh': '客场比赛',
                'es': 'Partido Fuera'
            },
            'opponent': {
                'ko': '상대팀',
                'en': 'Opponent',
                'ja': '対戦相手',
                'zh': '对手',
                'es': 'Oponente'
            },
            'predict_score': {
                'ko': '점수 예측',
                'en': 'Predict Score',
                'ja': 'スコア予測',
                'zh': '预测比分',
                'es': 'Predecir Puntuación'
            },
            'win_rate': {
                'ko': '승률',
                'en': 'Win Rate',
                'ja': '勝率',
                'zh': '胜率',
                'es': 'Tasa de Victoria'
            },
            'draw': {
                'ko': '무승부',
                'en': 'Draw',
                'ja': '引き分け',
                'zh': '平局',
                'es': 'Empate'
            },
            
            # 부상 리포트 관련
            'injury_report_title': {
                'ko': '부상 리포트',
                'en': 'Injury Report',
                'ja': '怪我レポート',
                'zh': '伤病报告',
                'es': 'Informe de Lesiones'
            },
            'realtime_injury_info': {
                'ko': '실시간 부상 정보',
                'en': 'Real-time Injury Information',
                'ja': 'リアルタイム怪我情報',
                'zh': '实时伤病信息',
                'es': 'Información de Lesiones en Tiempo Real'
            },
            'injury_summary': {
                'ko': '전체 리그 부상 현황',
                'en': 'League-wide Injury Status',
                'ja': 'リーグ全体怪我状況',
                'zh': '联赛伤病状况',
                'es': 'Estado de Lesiones de la Liga'
            },
            'total_injured': {
                'ko': '총 부상 선수',
                'en': 'Total Injured Players',
                'ja': '総負傷者',
                'zh': '总伤员',
                'es': 'Total de Jugadores Lesionados'
            },
            'team_injuries': {
                'ko': '팀별 부상 선수',
                'en': 'Team Injuries',
                'ja': 'チーム別負傷者',
                'zh': '球队伤员',
                'es': 'Lesiones del Equipo'
            },
            'all_teams': {
                'ko': '전체 팀',
                'en': 'All Teams',
                'ja': '全チーム',
                'zh': '所有球队',
                'es': 'Todos los Equipos'
            },
            'injury_description': {
                'ko': '부상',
                'en': 'Injury',
                'ja': '怪我',
                'zh': '伤病',
                'es': 'Lesión'
            },
            'expected_return': {
                'ko': '예상 복귀',
                'en': 'Expected Return',
                'ja': '復帰予定',
                'zh': '预计复出',
                'es': 'Retorno Esperado'
            },
            'no_injuries': {
                'ko': '현재 부상 선수가 없습니다',
                'en': 'No injured players currently',
                'ja': '現在負傷者なし',
                'zh': '目前无伤员',
                'es': 'No hay jugadores lesionados actualmente'
            },
            'player_search': {
                'ko': '선수 부상 상태 검색',
                'en': 'Player Injury Status Search',
                'ja': '選手怪我状態検索',
                'zh': '球员伤病状态搜索',
                'es': 'Búsqueda de Estado de Lesión del Jugador'
            },
            'player_name_input': {
                'ko': '선수 이름 입력',
                'en': 'Enter Player Name',
                'ja': '選手名入力',
                'zh': '输入球员姓名',
                'es': 'Ingresar Nombre del Jugador'
            },
            'player_injured': {
                'ko': '는 현재 부상 상태입니다',
                'en': 'is currently injured',
                'ja': 'は現在負傷中です',
                'zh': '目前受伤',
                'es': 'está actualmente lesionado'
            },
            'player_healthy': {
                'ko': '는 현재 건강한 상태입니다',
                'en': 'is currently healthy',
                'ja': 'は現在健康です',
                'zh': '目前健康',
                'es': 'está actualmente sano'
            },
            'last_updated': {
                'ko': '마지막 업데이트',
                'en': 'Last Updated',
                'ja': '最終更新',
                'zh': '最后更新',
                'es': 'Última Actualización'
            },
            
            # 코칭스태프 관련
            'coaching_staff_title': {
                'ko': '코칭스태프',
                'en': 'Coaching Staff',
                'ja': 'コーチングスタッフ',
                'zh': '教练组',
                'es': 'Cuerpo Técnico'
            },
            'coaching_info': {
                'ko': '코칭스태프 정보',
                'en': 'Coaching Staff Information',
                'ja': 'コーチングスタッフ情報',
                'zh': '教练组信息',
                'es': 'Información del Cuerpo Técnico'
            },
            'coaching_summary': {
                'ko': '전체 리그 코칭스태프 현황',
                'en': 'League-wide Coaching Staff Status',
                'ja': 'リーグ全体コーチングスタッフ状況',
                'zh': '联赛教练组状况',
                'es': 'Estado del Cuerpo Técnico de la Liga'
            },
            'total_teams': {
                'ko': '총 팀 수',
                'en': 'Total Teams',
                'ja': '総チーム数',
                'zh': '总球队数',
                'es': 'Total de Equipos'
            },
            'total_coaches': {
                'ko': '총 코치 수',
                'en': 'Total Coaches',
                'ja': '総コーチ数',
                'zh': '总教练数',
                'es': 'Total de Entrenadores'
            },
            'avg_coaches': {
                'ko': '팀당 평균 코치',
                'en': 'Average Coaches per Team',
                'ja': 'チーム平均コーチ',
                'zh': '每队平均教练',
                'es': 'Promedio de Entrenadores por Equipo'
            },
            'assistant_coaches': {
                'ko': '코치진',
                'en': 'Assistant Coaches',
                'ja': 'アシスタントコーチ',
                'zh': '助理教练',
                'es': 'Entrenadores Asistentes'
            },
            'coach_search': {
                'ko': '감독 검색',
                'en': 'Coach Search',
                'ja': '監督検索',
                'zh': '教练搜索',
                'es': 'Búsqueda de Entrenador'
            },
            'coach_name_input': {
                'ko': '감독 이름 입력',
                'en': 'Enter Coach Name',
                'ja': '監督名入力',
                'zh': '输入教练姓名',
                'es': 'Ingresar Nombre del Entrenador'
            },
            'coach_found': {
                'ko': '를 찾았습니다',
                'en': 'found',
                'ja': 'が見つかりました',
                'zh': '找到',
                'es': 'encontrado'
            },
            'coach_not_found': {
                'ko': '를 찾을 수 없습니다',
                'en': 'not found',
                'ja': 'が見つかりません',
                'zh': '未找到',
                'es': 'no encontrado'
            },
            
            # 설정 관련
            'system_settings': {
                'ko': '시스템 설정',
                'en': 'System Settings',
                'ja': 'システム設定',
                'zh': '系统设置',
                'es': 'Configuración del Sistema'
            },
            'data_source_settings': {
                'ko': '데이터 소스 설정',
                'en': 'Data Source Settings',
                'ja': 'データソース設定',
                'zh': '数据源设置',
                'es': 'Configuración de Fuente de Datos'
            },
            'prediction_model_settings': {
                'ko': '예측 모델 설정',
                'en': 'Prediction Model Settings',
                'ja': '予測モデル設定',
                'zh': '预测模型设置',
                'es': 'Configuración del Modelo de Predicción'
            },
            'save_settings': {
                'ko': '설정 저장',
                'en': 'Save Settings',
                'ja': '設定保存',
                'zh': '保存设置',
                'es': 'Guardar Configuración'
            },
            'settings_saved': {
                'ko': '설정이 저장되었습니다',
                'en': 'Settings saved',
                'ja': '設定が保存されました',
                'zh': '设置已保存',
                'es': 'Configuración guardada'
            },
            'supported_languages': {
                'ko': '지원 언어',
                'en': 'Supported Languages',
                'ja': '対応言語',
                'zh': '支持的语言',
                'es': 'Idiomas Soportados'
            },
            
            # 기타 메시지
            'error_occurred': {
                'ko': '오류가 발생했습니다',
                'en': 'An error occurred',
                'ja': 'エラーが発生しました',
                'zh': '发生错误',
                'es': 'Ocurrió un error'
            },
            'no_data_available': {
                'ko': '데이터를 사용할 수 없습니다',
                'en': 'No data available',
                'ja': 'データがありません',
                'zh': '无可用数据',
                'es': 'No hay datos disponibles'
            },
            'fetching_data': {
                'ko': '데이터를 가져오는 중',
                'en': 'Fetching data',
                'ja': 'データ取得中',
                'zh': '正在获取数据',
                'es': 'Obteniendo datos'
            },
            'matches': {
                'ko': '경기',
                'en': 'matches',
                'ja': '試合',
                'zh': '场比赛',
                'es': 'partidos'
            },
            'teams': {
                'ko': '팀',
                'en': 'teams',
                'ja': 'チーム',
                'zh': '队',
                'es': 'equipos'
            },
            'players': {
                'ko': '명',
                'en': 'players',
                'ja': '名',
                'zh': '名球员',
                'es': 'jugadores'
            },
            
            # 후원 및 광고
            'support_coffee': {
                'ko': '☕ 커피 한 잔 후원하기',
                'en': '☕ Buy Me a Coffee',
                'ja': '☕ コーヒーをおごる',
                'zh': '☕ 请我喝咖啡',
                'es': '☕ Invítame un Café'
            },
            'support_message': {
                'ko': '이 프로젝트가 도움이 되셨나요? 커피 한 잔으로 응원해주세요!',
                'en': 'Did this project help you? Support with a coffee!',
                'ja': 'このプロジェクトは役に立ちましたか？コーヒーで応援してください！',
                'zh': '这个项目对您有帮助吗？请用一杯咖啡支持我！',
                'es': '¿Te ayudó este proyecto? ¡Apóyalo con un café!'
            },
            'ad_space': {
                'ko': '광고 공간',
                'en': 'Advertisement Space',
                'ja': '広告スペース',
                'zh': '广告位',
                'es': 'Espacio Publicitario'
            },
            'sponsor_message': {
                'ko': '스폰서 및 광고 문의',
                'en': 'Sponsor & Ad Inquiries',
                'ja': 'スポンサー・広告のお問い合わせ',
                'zh': '赞助商和广告咨询',
                'es': 'Consultas de Patrocinio y Publicidad'
            },
            
            # Tab4 - 경기 일정 추가 번역
            'schedule_mode': {
                'ko': '일정 보기 모드',
                'en': 'Schedule View Mode',
                'ja': 'スケジュール表示モード',
                'zh': '日程查看模式',
                'es': 'Modo de Vista de Calendario'
            },
            'all_schedule': {
                'ko': '전체 일정',
                'en': 'All Schedules',
                'ja': '全スケジュール',
                'zh': '全部日程',
                'es': 'Todos los Calendarios'
            },
            'league_schedule_title': {
                'ko': '🏆 리그별 경기 일정',
                'en': '🏆 League Schedule',
                'ja': '🏆 リーグ別スケジュール',
                'zh': '🏆 联赛日程',
                'es': '🏆 Calendario de Liga'
            },
            'team_next_matches': {
                'ko': '👥 팀별 다음 경기',
                'en': '👥 Team Next Matches',
                'ja': '👥 チーム別次の試合',
                'zh': '👥 球队下一场比赛',
                'es': '👥 Próximos Partidos del Equipo'
            },
            'loading_schedule': {
                'ko': '실시간 경기 일정 가져오는 중...',
                'en': 'Loading real-time schedule...',
                'ja': 'リアルタイムスケジュール読み込み中...',
                'zh': '正在加载实时日程...',
                'es': 'Cargando calendario en tiempo real...'
            },
            'upcoming': {
                'ko': '다가오는 ',
                'en': 'Upcoming ',
                'ja': '今後の',
                'zh': '即将',
                'es': 'Próximos '
            },
            'next_matches_of': {
                'ko': '의 다음 ',
                'en': '\'s next ',
                'ja': 'の次の',
                'zh': '的下一场',
                'es': ' próximos '
            },
            'date_label': {
                'ko': '**날짜:**',
                'en': '**Date:**',
                'ja': '**日付:**',
                'zh': '**日期:**',
                'es': '**Fecha:**'
            },
            'time_label': {
                'ko': '**시간:**',
                'en': '**Time:**',
                'ja': '**時間:**',
                'zh': '**时间:**',
                'es': '**Hora:**'
            },
            'venue_label': {
                'ko': '**장소:**',
                'en': '**Venue:**',
                'ja': '**会場:**',
                'zh': '**场地:**',
                'es': '**Estadio:**'
            },
            'broadcast_label': {
                'ko': '**중계:**',
                'en': '**TV:**',
                'ja': '**放送:**',
                'zh': '**转播:**',
                'es': '**Transmisión:**'
            },
            'status_label': {
                'ko': '상태: ',
                'en': 'Status: ',
                'ja': '状態: ',
                'zh': '状态: ',
                'es': 'Estado: '
            },
            'opponent_label': {
                'ko': '**상대팀:**',
                'en': '**Opponent:**',
                'ja': '**対戦相手:**',
                'zh': '**对手:**',
                'es': '**Oponente:**'
            },
            'expected_score_label': {
                'ko': '**예상 점수: ',
                'en': '**Expected Score: ',
                'ja': '**予想スコア: ',
                'zh': '**预期比分: ',
                'es': '**Puntuación Esperada: '
            },
            'win_rate_label': {
                'ko': '승률: ',
                'en': 'Win Rate: ',
                'ja': '勝率: ',
                'zh': '胜率: ',
                'es': 'Tasa de Victoria: '
            },
            'draw_label': {
                'ko': '무승부: ',
                'en': 'Draw: ',
                'ja': '引き分け: ',
                'zh': '平局: ',
                'es': 'Empate: '
            },
            'team_data_not_found': {
                'ko': '⚠️ 팀 데이터를 찾을 수 없습니다.',
                'en': '⚠️ Team data not found.',
                'ja': '⚠️ チームデータが見つかりません。',
                'zh': '⚠️ 未找到球队数据。',
                'es': '⚠️ Datos del equipo no encontrados.'
            },
            'prediction_error': {
                'ko': '예측 오류: ',
                'en': 'Prediction error: ',
                'ja': '予測エラー: ',
                'zh': '预测错误: ',
                'es': 'Error de predicción: '
            },
            'cannot_load_schedule': {
                'ko': '의 실시간 일정을 가져올 수 없습니다.',
                'en': ' real-time schedule cannot be loaded.',
                'ja': 'のリアルタイムスケジュールを取得できません。',
                'zh': '无法加载实时日程。',
                'es': ' no se puede cargar el calendario en tiempo real.'
            },
            'schedule_module_error': {
                'ko': '❌ 경기 일정 모듈을 불러올 수 없습니다: ',
                'en': '❌ Cannot load schedule module: ',
                'ja': '❌ スケジュールモジュールを読み込めません: ',
                'zh': '❌ 无法加载日程模块: ',
                'es': '❌ No se puede cargar el módulo de calendario: '
            },
            'error_occurred': {
                'ko': '❌ 오류 발생: ',
                'en': '❌ Error occurred: ',
                'ja': '❌ エラー発生: ',
                'zh': '❌ 发生错误: ',
                'es': '❌ Ocurrió un error: '
            },
            'match': {
                'ko': '경기',
                'en': 'matches',
                'ja': '試合',
                'zh': '场比赛',
                'es': 'partidos'
            },
            'match_number': {
                'ko': '경기 ',
                'en': 'Match ',
                'ja': '試合',
                'zh': '比赛',
                'es': 'Partido '
            },
            
            # Tab5 - 부상 리포트 추가 번역
            'injury_report_support': {
                'ko': '⚠️ 부상 리포트는 현재 ',
                'en': '⚠️ Injury report currently supports ',
                'ja': '⚠️ 怪我レポートは現在',
                'zh': '⚠️ 伤病报告目前支持',
                'es': '⚠️ El informe de lesiones actualmente admite '
            },
            'leagues_only': {
                'ko': ' 리그만 지원합니다.',
                'en': ' leagues only.',
                'ja': 'リーグのみサポートしています。',
                'zh': '联赛。',
                'es': ' ligas solamente.'
            },
            'realtime_injury_data': {
                'ko': '📡 **실시간 부상 정보** - ESPN Injury Report에서 최신 선수 부상 상태를 가져옵니다.',
                'en': '📡 **Real-time Injury Data** - Fetching latest player injury status from ESPN Injury Report.',
                'ja': '📡 **リアルタイム怪我情報** - ESPN Injury Reportから最新の選手怪我状態を取得します。',
                'zh': '📡 **实时伤病数据** - 从ESPN伤病报告获取最新球员伤病状态。',
                'es': '📡 **Datos de Lesiones en Tiempo Real** - Obteniendo el estado de lesiones más reciente de ESPN Injury Report.'
            },
            'simulation_injury_data': {
                'ko': '📊 **시뮬레이션 부상 정보** - KBO 공식 부상 정보 (ESPN에서 KBO 데이터 미제공)',
                'en': '📊 **Simulated Injury Data** - KBO official injury information (ESPN does not provide KBO data)',
                'ja': '📊 **シミュレーション怪我情報** - KBO公式怪我情報（ESPNはKBOデータを提供していません）',
                'zh': '📊 **模拟伤病数据** - KBO官方伤病信息（ESPN不提供KBO数据）',
                'es': '📊 **Datos de Lesiones Simulados** - Información oficial de lesiones de KBO (ESPN no proporciona datos de KBO)'
            },
            'trying_realtime_injury': {
                'ko': '📡 **실시간 부상 정보 시도 중** - ESPN Soccer Injuries에서 데이터를 가져옵니다. 실패 시 시뮬레이션 데이터 사용.',
                'en': '📡 **Attempting Real-time Injury Data** - Fetching data from ESPN Soccer Injuries. Using simulated data if failed.',
                'ja': '📡 **リアルタイム怪我情報試行中** - ESPN Soccer Injuriesからデータを取得します。失敗時はシミュレーションデータを使用。',
                'zh': '📡 **尝试实时伤病数据** - 从ESPN足球伤病获取数据。失败时使用模拟数据。',
                'es': '📡 **Intentando Datos de Lesiones en Tiempo Real** - Obteniendo datos de ESPN Soccer Injuries. Usando datos simulados si falla.'
            },
            'refresh_injury_info': {
                'ko': '🔄 부상 정보 새로고침',
                'en': '🔄 Refresh Injury Info',
                'ja': '🔄 怪我情報更新',
                'zh': '🔄 刷新伤病信息',
                'es': '🔄 Actualizar Información de Lesiones'
            },
            'loading_injury_info': {
                'ko': '부상 정보를 가져오는 중...',
                'en': 'Loading injury information...',
                'ja': '怪我情報を取得中...',
                'zh': '正在加载伤病信息...',
                'es': 'Cargando información de lesiones...'
            },
            'league_injury_status': {
                'ko': '📊 전체 리그 부상 현황',
                'en': '📊 League-wide Injury Status',
                'ja': '📊 リーグ全体怪我状況',
                'zh': '📊 联赛伤病状况',
                'es': '📊 Estado de Lesiones de la Liga'
            },
            'total_injured_players': {
                'ko': '총 부상 선수',
                'en': 'Total Injured Players',
                'ja': '総負傷者',
                'zh': '总伤员',
                'es': 'Total de Jugadores Lesionados'
            },
            'out_status': {
                'ko': '결장 (Out)',
                'en': 'Out',
                'ja': '欠場',
                'zh': '缺阵',
                'es': 'Fuera'
            },
            'day_to_day_status': {
                'ko': '일일 점검 (Day-to-Day)',
                'en': 'Day-to-Day',
                'ja': '日々確認',
                'zh': '每日观察',
                'es': 'Día a Día'
            },
            'questionable_status': {
                'ko': '출전 불투명 (Questionable)',
                'en': 'Questionable',
                'ja': '出場不透明',
                'zh': '出场存疑',
                'es': 'Dudoso'
            },
            'last_updated_label': {
                'ko': '마지막 업데이트: ',
                'en': 'Last Updated: ',
                'ja': '最終更新: ',
                'zh': '最后更新: ',
                'es': 'Última Actualización: '
            },
            'team_injured_players': {
                'ko': ' 팀의 부상 선수: ',
                'en': ' team injured players: ',
                'ja': 'チームの負傷者: ',
                'zh': '队伤员: ',
                'es': ' jugadores lesionados del equipo: '
            },
            'status_label2': {
                'ko': '   상태: ',
                'en': '   Status: ',
                'ja': '   状態: ',
                'zh': '   状态: ',
                'es': '   Estado: '
            },
            'injury_label2': {
                'ko': '   부상: ',
                'en': '   Injury: ',
                'ja': '   怪我: ',
                'zh': '   伤病: ',
                'es': '   Lesión: '
            },
            'expected_return_label2': {
                'ko': '   예상 복귀: ',
                'en': '   Expected Return: ',
                'ja': '   復帰予定: ',
                'zh': '   预计复出: ',
                'es': '   Retorno Esperado: '
            },
            'expected_return_label': {
                'ko': '**예상 복귀:**',
                'en': '**Expected Return:**',
                'ja': '**復帰予定:**',
                'zh': '**预计复出:**',
                'es': '**Retorno Esperado:**'
            },
            'position_label': {
                'ko': '**포지션:**',
                'en': '**Position:**',
                'ja': '**ポジション:**',
                'zh': '**位置:**',
                'es': '**Posición:**'
            },
            'no_injured_players': {
                'ko': ' 팀에는 현재 부상 선수가 없습니다!',
                'en': ' team has no injured players currently!',
                'ja': 'チームには現在負傷者がいません！',
                'zh': '队目前没有伤员！',
                'es': ' equipo no tiene jugadores lesionados actualmente!'
            },
            'player_injury_search': {
                'ko': '🔍 선수 부상 상태 검색',
                'en': '🔍 Player Injury Status Search',
                'ja': '🔍 選手怪我状態検索',
                'zh': '🔍 球员伤病状态搜索',
                'es': '🔍 Búsqueda de Estado de Lesión del Jugador'
            },
            'enter_player_name': {
                'ko': '선수 이름 입력',
                'en': 'Enter player name',
                'ja': '選手名入力',
                'zh': '输入球员姓名',
                'es': 'Ingresar nombre del jugador'
            },
            'is_injured': {
                'ko': '는 현재 부상 상태입니다.',
                'en': ' is currently injured.',
                'ja': 'は現在負傷中です。',
                'zh': '目前受伤。',
                'es': ' está actualmente lesionado.'
            },
            'is_healthy': {
                'ko': '는 현재 건강한 상태입니다!',
                'en': ' is currently healthy!',
                'ja': 'は現在健康です！',
                'zh': '目前健康！',
                'es': ' está actualmente sano!'
            },
            'injury_info_error': {
                'ko': '❌ 부상 정보를 가져오는 중 오류가 발생했습니다: ',
                'en': '❌ Error fetching injury information: ',
                'ja': '❌ 怪我情報取得中にエラーが発生しました: ',
                'zh': '❌ 获取伤病信息时发生错误: ',
                'es': '❌ Error al obtener información de lesiones: '
            },
            'espn_access_error': {
                'ko': '💡 ESPN 웹사이트에 접근할 수 없거나 데이터 형식이 변경되었을 수 있습니다.',
                'en': '💡 Cannot access ESPN website or data format may have changed.',
                'ja': '💡 ESPNウェブサイトにアクセスできないか、データ形式が変更された可能性があります。',
                'zh': '💡 无法访问ESPN网站或数据格式可能已更改。',
                'es': '💡 No se puede acceder al sitio web de ESPN o el formato de datos puede haber cambiado.'
            },
            'kbo_simulation_data': {
                'ko': '💡 KBO 부상 정보는 시뮬레이션 데이터를 사용합니다.',
                'en': '💡 KBO injury information uses simulated data.',
                'ja': '💡 KBO怪我情報はシミュレーションデータを使用します。',
                'zh': '💡 KBO伤病信息使用模拟数据。',
                'es': '💡 La información de lesiones de KBO utiliza datos simulados.'
            },
            'realtime_data_failed': {
                'ko': '💡 실시간 데이터 수집 실패. 시뮬레이션 데이터를 사용합니다.',
                'en': '💡 Real-time data collection failed. Using simulated data.',
                'ja': '💡 リアルタイムデータ収集失敗。シミュレーションデータを使用します。',
                'zh': '💡 实时数据收集失败。使用模拟数据。',
                'es': '💡 Falló la recolección de datos en tiempo real. Usando datos simulados.'
            },
            
            # Tab6 - 코칭스태프 추가 번역
            'coaching_staff_support': {
                'ko': '⚠️ 코칭스태프 정보는 현재 ',
                'en': '⚠️ Coaching staff information currently supports ',
                'ja': '⚠️ コーチングスタッフ情報は現在',
                'zh': '⚠️ 教练组信息目前支持',
                'es': '⚠️ La información del cuerpo técnico actualmente admite '
            },
            'coaching_staff_info_desc': {
                'ko': '📊 **코칭스태프 정보** - 각 팀의 감독 및 코치진 정보를 제공합니다.',
                'en': '📊 **Coaching Staff Information** - Provides head coach and coaching staff information for each team.',
                'ja': '📊 **コーチングスタッフ情報** - 各チームの監督とコーチ陣情報を提供します。',
                'zh': '📊 **教练组信息** - 提供每支球队的主教练和教练组信息。',
                'es': '📊 **Información del Cuerpo Técnico** - Proporciona información del entrenador principal y cuerpo técnico de cada equipo.'
            },
            'refresh_coaching_staff': {
                'ko': '🔄 코칭스태프 새로고침',
                'en': '🔄 Refresh Coaching Staff',
                'ja': '🔄 コーチングスタッフ更新',
                'zh': '🔄 刷新教练组',
                'es': '🔄 Actualizar Cuerpo Técnico'
            },
            'loading_coaching_staff': {
                'ko': '코칭스태프 정보를 가져오는 중...',
                'en': 'Loading coaching staff information...',
                'ja': 'コーチングスタッフ情報を取得中...',
                'zh': '正在加载教练组信息...',
                'es': 'Cargando información del cuerpo técnico...'
            },
            'league_coaching_status': {
                'ko': '📊 전체 리그 코칭스태프 현황',
                'en': '📊 League-wide Coaching Staff Status',
                'ja': '📊 リーグ全体コーチングスタッフ状況',
                'zh': '📊 联赛教练组状况',
                'es': '📊 Estado del Cuerpo Técnico de la Liga'
            },
            'total_teams_count': {
                'ko': '총 팀 수',
                'en': 'Total Teams',
                'ja': '総チーム数',
                'zh': '总球队数',
                'es': 'Total de Equipos'
            },
            'total_coaches_count': {
                'ko': '총 코치 수',
                'en': 'Total Coaches',
                'ja': '総コーチ数',
                'zh': '总教练数',
                'es': 'Total de Entrenadores'
            },
            'avg_coaches_per_team': {
                'ko': '팀당 평균 코치',
                'en': 'Average Coaches per Team',
                'ja': 'チーム平均コーチ',
                'zh': '每队平均教练',
                'es': 'Promedio de Entrenadores por Equipo'
            },
            'head_coach_title': {
                'ko': '### 👨‍💼 감독',
                'en': '### 👨‍💼 Head Coach',
                'ja': '### 👨‍💼 監督',
                'zh': '### 👨‍💼 主教练',
                'es': '### 👨‍💼 Entrenador Principal'
            },
            'coaches_title': {
                'ko': '### 👥 코치진',
                'en': '### 👥 Coaching Staff',
                'ja': '### 👥 コーチ陣',
                'zh': '### 👥 教练组',
                'es': '### 👥 Cuerpo Técnico'
            },
            'updated_label': {
                'ko': '업데이트: ',
                'en': 'Updated: ',
                'ja': '更新: ',
                'zh': '更新: ',
                'es': 'Actualizado: '
            },
            'head_coach_section': {
                'ko': '👨‍💼 감독',
                'en': '👨‍💼 Head Coach',
                'ja': '👨‍💼 監督',
                'zh': '👨‍💼 主教练',
                'es': '👨‍💼 Entrenador Principal'
            },
            'coaches_section': {
                'ko': '👥 코치진',
                'en': '👥 Coaching Staff',
                'ja': '👥 コーチ陣',
                'zh': '👥 教练组',
                'es': '👥 Cuerpo Técnico'
            },
            'total_label': {
                'ko': '**총 ',
                'en': '**Total ',
                'ja': '**合計',
                'zh': '**总共',
                'es': '**Total '
            },
            'coaching_staff_not_found': {
                'ko': ' 팀의 코칭스태프 정보를 찾을 수 없습니다.',
                'en': ' team coaching staff information not found.',
                'ja': 'チームのコーチングスタッフ情報が見つかりません。',
                'zh': '队教练组信息未找到。',
                'es': ' información del cuerpo técnico del equipo no encontrada.'
            },
            'coach_search_title': {
                'ko': '🔍 감독 검색',
                'en': '🔍 Coach Search',
                'ja': '🔍 監督検索',
                'zh': '🔍 教练搜索',
                'es': '🔍 Búsqueda de Entrenador'
            },
            'enter_coach_name': {
                'ko': '감독 이름 입력',
                'en': 'Enter coach name',
                'ja': '監督名入力',
                'zh': '输入教练姓名',
                'es': 'Ingresar nombre del entrenador'
            },
            'found_in_teams': {
                'ko': '개 팀에서 \'',
                'en': ' teams found \'',
                'ja': 'チームで「',
                'zh': '支球队找到"',
                'es': ' equipos encontraron \''
            },
            'found_text': {
                'ko': '\'를 찾았습니다.',
                'en': '\' found.',
                'ja': '」が見つかりました。',
                'zh': '"。',
                'es': '\' encontrado.'
            },
            'team_label': {
                'ko': '**팀:**',
                'en': '**Team:**',
                'ja': '**チーム:**',
                'zh': '**球队:**',
                'es': '**Equipo:**'
            },
            'coach_label2': {
                'ko': '**감독:**',
                'en': '**Head Coach:**',
                'ja': '**監督:**',
                'zh': '**主教练:**',
                'es': '**Entrenador Principal:**'
            },
            'coaches_label2': {
                'ko': '**코치진:**',
                'en': '**Coaches:**',
                'ja': '**コーチ陣:**',
                'zh': '**教练组:**',
                'es': '**Cuerpo Técnico:**'
            },
            'not_found_text': {
                'ko': '\'를 찾을 수 없습니다.',
                'en': '\' not found.',
                'ja': '」が見つかりません。',
                'zh': '"未找到。',
                'es': '\' no encontrado.'
            },
            'coaching_staff_error': {
                'ko': '❌ 코칭스태프 정보를 가져오는 중 오류가 발생했습니다: ',
                'en': '❌ Error fetching coaching staff information: ',
                'ja': '❌ コーチングスタッフ情報取得中にエラーが発生しました: ',
                'zh': '❌ 获取教练组信息时发生错误: ',
                'es': '❌ Error al obtener información del cuerpo técnico: '
            },
            
            # Tab7 - 설정 추가 번역
            'data_source_settings_title': {
                'ko': '데이터 소스 설정',
                'en': 'Data Source Settings',
                'ja': 'データソース設定',
                'zh': '数据源设置',
                'es': 'Configuración de Fuente de Datos'
            },
            'enable_web_scraping': {
                'ko': '웹 크롤링 활성화',
                'en': 'Enable Web Scraping',
                'ja': 'ウェブクローリング有効化',
                'zh': '启用网页抓取',
                'es': 'Habilitar Web Scraping'
            },
            'enable_api_data': {
                'ko': 'API 데이터 수집',
                'en': 'API Data Collection',
                'ja': 'APIデータ収集',
                'zh': 'API数据收集',
                'es': 'Recolección de Datos API'
            },
            'api_key_label': {
                'ko': 'API 키',
                'en': 'API Key',
                'ja': 'APIキー',
                'zh': 'API密钥',
                'es': 'Clave API'
            },
            'prediction_model_settings_title': {
                'ko': '예측 모델 설정',
                'en': 'Prediction Model Settings',
                'ja': '予測モデル設定',
                'zh': '预测模型设置',
                'es': 'Configuración del Modelo de Predicción'
            },
            'select_model_label': {
                'ko': '모델 선택',
                'en': 'Select Model',
                'ja': 'モデル選択',
                'zh': '选择模型',
                'es': 'Seleccionar Modelo'
            },
            'ensemble_model': {
                'ko': '앙상블',
                'en': 'Ensemble',
                'ja': 'アンサンブル',
                'zh': '集成',
                'es': 'Conjunto'
            },
            'historical_data_range': {
                'ko': '과거 데이터 범위 (경기 수)',
                'en': 'Historical Data Range (Number of Matches)',
                'ja': '過去データ範囲（試合数）',
                'zh': '历史数据范围（比赛数）',
                'es': 'Rango de Datos Históricos (Número de Partidos)'
            },
            'save_settings_button': {
                'ko': '설정 저장',
                'en': 'Save Settings',
                'ja': '設定保存',
                'zh': '保存设置',
                'es': 'Guardar Configuración'
            },
            'settings_saved_message': {
                'ko': '설정이 저장되었습니다!',
                'en': 'Settings saved!',
                'ja': '設定が保存されました！',
                'zh': '设置已保存！',
                'es': '¡Configuración guardada!'
            },
            
            # 푸터 및 기타
            'footer_title': {
                'ko': '📡 VIBE BOX Sports MatchSignal - 실시간 스포츠 경기 예측 및 분석 플랫폼',
                'en': '📡 VIBE BOX Sports MatchSignal - Real-time Sports Match Prediction & Analysis Platform',
                'ja': '📡 VIBE BOX Sports MatchSignal - リアルタイムスポーツ試合予測・分析プラットフォーム',
                'zh': '📡 VIBE BOX Sports MatchSignal - 实时体育比赛预测和分析平台',
                'es': '📡 VIBE BOX Sports MatchSignal - Plataforma de Predicción y Análisis de Partidos Deportivos en Tiempo Real'
            },
            'footer_disclaimer': {
                'ko': '⚠️ 본 시스템은 참고용 분석 도구입니다. 투자 결정에 대한 책임은 사용자에게 있습니다.',
                'en': '⚠️ This system is a reference analysis tool. Users are responsible for investment decisions.',
                'ja': '⚠️ 本システムは参考用分析ツールです。投資決定の責任はユーザーにあります。',
                'zh': '⚠️ 本系统是参考分析工具。用户对投资决策负责。',
                'es': '⚠️ Este sistema es una herramienta de análisis de referencia. Los usuarios son responsables de las decisiones de inversión.'
            },
            'fatigue_label': {
                'ko': '피로도',
                'en': 'Fatigue',
                'ja': '疲労度',
                'zh': '疲劳度',
                'es': 'Fatiga'
            },
            'condition_index_label': {
                'ko': '컨디션 지수',
                'en': 'Condition Index',
                'ja': 'コンディション指数',
                'zh': '状态指数',
                'es': 'Índice de Condición'
            },
            'recent_5_rating': {
                'ko': '최근 5경기 평점',
                'en': 'Recent 5 Games Rating',
                'ja': '最近5試合評価',
                'zh': '最近5场评分',
                'es': 'Calificación Últimos 5 Partidos'
            },
            'injury_risk_label': {
                'ko': '부상 위험도',
                'en': 'Injury Risk',
                'ja': '怪我リスク',
                'zh': '受伤风险',
                'es': 'Riesgo de Lesión'
            },
            'performance_trend_label': {
                'ko': '📈 퍼포먼스 트렌드',
                'en': '📈 Performance Trend',
                'ja': '📈 パフォーマンストレンド',
                'zh': '📈 表现趋势',
                'es': '📈 Tendencia de Rendimiento'
            },
            'coaching_staff_load_failed': {
                'ko': '코칭스태프 정보 로드 실패: ',
                'en': 'Failed to load coaching staff info: ',
                'ja': 'コーチングスタッフ情報読み込み失敗: ',
                'zh': '加载教练组信息失败: ',
                'es': 'Error al cargar información del cuerpo técnico: '
            },
            'injured_count_label': {
                'ko': '부상자: ',
                'en': 'Injured: ',
                'ja': '負傷者: ',
                'zh': '伤员: ',
                'es': 'Lesionados: '
            },
            'injury_info_collection_failed': {
                'ko': '부상 정보 수집 실패: ',
                'en': 'Failed to collect injury info: ',
                'ja': '怪我情報収集失敗: ',
                'zh': '收集伤病信息失败: ',
                'es': 'Error al recopilar información de lesiones: '
            },
            'expected_score_basic': {
                'ko': '🎲 예상 스코어 (기본 예측)',
                'en': '🎲 Expected Score (Basic Prediction)',
                'ja': '🎲 予想スコア（基本予測）',
                'zh': '🎲 预期比分（基本预测）',
                'es': '🎲 Puntuación Esperada (Predicción Básica)'
            },
            'detailed_score_prediction_title': {
                'ko': '🎯 상세 점수 예측',
                'en': '🎯 Detailed Score Prediction',
                'ja': '🎯 詳細スコア予測',
                'zh': '🎯 详细比分预测',
                'es': '🎯 Predicción Detallada de Puntuación'
            },
            'draw_probability_label': {
                'ko': '⚖️ 무승부 확률: ',
                'en': '⚖️ Draw Probability: ',
                'ja': '⚖️ 引き分け確率: ',
                'zh': '⚖️ 平局概率: ',
                'es': '⚖️ Probabilidad de Empate: '
            },
            'prediction_confidence_label2': {
                'ko': '**예측 신뢰도:**',
                'en': '**Prediction Confidence:**',
                'ja': '**予測信頼度:**',
                'zh': '**预测置信度:**',
                'es': '**Confianza de Predicción:**'
            },
            'view_prediction_basis': {
                'ko': '📊 예측 근거 보기',
                'en': '📊 View Prediction Basis',
                'ja': '📊 予測根拠を見る',
                'zh': '📊 查看预测依据',
                'es': '📊 Ver Base de Predicción'
            },
            'expected_total_points': {
                'ko': '**총 득점 예상:**',
                'en': '**Expected Total Points:**',
                'ja': '**総得点予想:**',
                'zh': '**预期总得分:**',
                'es': '**Puntos Totales Esperados:**'
            },
            'points_unit': {
                'ko': '점',
                'en': ' pts',
                'ja': 'ポイント',
                'zh': '分',
                'es': ' pts'
            },
            'score_difference_label': {
                'ko': '**점수 차이:**',
                'en': '**Score Difference:**',
                'ja': '**スコア差:**',
                'zh': '**比分差:**',
                'es': '**Diferencia de Puntuación:**'
            },
            'expected_total_goals': {
                'ko': '**총 골 예상:**',
                'en': '**Expected Total Goals:**',
                'ja': '**総ゴール予想:**',
                'zh': '**预期总进球:**',
                'es': '**Goles Totales Esperados:**'
            },
            'goals_unit': {
                'ko': '골',
                'en': ' goals',
                'ja': 'ゴール',
                'zh': '球',
                'es': ' goles'
            },
            'score_prediction_error': {
                'ko': '⚠️ 점수 예측 중 오류 발생: ',
                'en': '⚠️ Error during score prediction: ',
                'ja': '⚠️ スコア予測中にエラー発生: ',
                'zh': '⚠️ 比分预测时发生错误: ',
                'es': '⚠️ Error durante la predicción de puntuación: '
            },
            'injury_info_applied': {
                'ko': '⚕️ 실시간 부상 선수 정보가 예측에 반영되었습니다.',
                'en': '⚕️ Real-time injury information has been applied to the prediction.',
                'ja': '⚕️ リアルタイム怪我情報が予測に反映されました。',
                'zh': '⚕️ 实时伤病信息已应用于预测。',
                'es': '⚕️ La información de lesiones en tiempo real se ha aplicado a la predicción.'
            },
            'injury_info_applied2': {
                'ko': '⚕️ 부상 선수 정보가 예측에 반영되었습니다.',
                'en': '⚕️ Injury information has been applied to the prediction.',
                'ja': '⚕️ 怪我情報が予測に反映されました。',
                'zh': '⚕️ 伤病信息已应用于预测。',
                'es': '⚕️ La información de lesiones se ha aplicado a la predicción.'
            },
            'confidence_high': {
                'ko': '높음',
                'en': 'High',
                'ja': '高',
                'zh': '高',
                'es': 'Alto'
            },
            'confidence_medium': {
                'ko': '중간',
                'en': 'Medium',
                'ja': '中',
                'zh': '中',
                'es': 'Medio'
            },
            'confidence_low': {
                'ko': '낮음',
                'en': 'Low',
                'ja': '低',
                'zh': '低',
                'es': 'Bajo'
            },
            'people_unit': {
                'ko': '명',
                'en': '',
                'ja': '名',
                'zh': '人',
                'es': ''
            },
            'team_unit': {
                'ko': '팀',
                'en': ' teams',
                'ja': 'チーム',
                'zh': '队',
                'es': ' equipos'
            },
            'example_prefix': {
                'ko': '예: ',
                'en': 'e.g.: ',
                'ja': '例: ',
                'zh': '例如: ',
                'es': 'ej.: '
            },
        }
    
    def get(self, key, default=None):
        """번역 텍스트 가져오기"""
        if key in self.translations:
            return self.translations[key].get(self.language, self.translations[key].get('en', default or key))
        return default or key
    
    def set_language(self, language):
        """언어 변경"""
        if language in ['ko', 'en', 'ja', 'zh', 'es']:
            self.language = language
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def get_available_languages(self):
        """사용 가능한 언어 목록"""
        return {
            'ko': '한국어 (Korean)',
            'en': 'English',
            'ja': '日本語 (Japanese)',
            'zh': '中文 (Chinese)',
            'es': 'Español (Spanish)'
        }


# 전역 번역기 인스턴스
_translator = None

def get_translator(language='ko'):
    """번역기 인스턴스 가져오기"""
    global _translator
    if _translator is None or _translator.language != language:
        _translator = Translator(language)
    return _translator

def t(key, language='ko'):
    """간단한 번역 함수"""
    translator = get_translator(language)
    return translator.get(key)
