// 卦象数据
const guaList = [
    "乾", "坤", "屯", "蒙", "需", "讼", "师", "比",
    "小畜", "履", "泰", "否", "同人", "大有", "谦", "豫",
    "随", "蛊", "临", "观", "噬嗑", "贲", "剥", "复",
    "无妄", "大畜", "颐", "大过", "坎", "离", "咸", "恒",
    "遁", "大壮", "晋", "明夷", "家人", "睽", "蹇", "解",
    "损", "益", "夬", "姤", "萃", "升", "困", "井",
    "革", "鼎", "震", "艮", "渐", "归妹", "丰", "旅",
    "巽", "兑", "涣", "节", "中孚", "小过", "既济", "未济"
];

// 卦象索引映射
const guaIndex = [
    [0, 1, 2, 3, 4, 5, 6, 7],
    [8, 9, 10, 11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20, 21, 22, 23],
    [24, 25, 26, 27, 28, 29, 30, 31],
    [32, 33, 34, 35, 36, 37, 38, 39],
    [40, 41, 42, 43, 44, 45, 46, 47],
    [48, 49, 50, 51, 52, 53, 54, 55],
    [56, 57, 58, 59, 60, 61, 62, 63]
];

// 今日推荐问题
const todayQuestions = [
    "今日运势如何？",
    "工作上有什么需要注意的？",
    "感情方面会有什么发展？",
    "财运如何？",
    "健康状况怎样？",
    "学业进展如何？",
    "人际关系如何处理？",
    "投资理财有什么建议？"
];

// 全局状态
let currentQuestion = '';
let hexagramResult = null;
let isAnimating = false;
let coinResults = [];
let totalRounds = 6;
let hexagramList = []; // 改用类似divination项目的HexagramObj数组
let lastFaces = [true, true, true]; // 记录上次三枚硬币朝向：true=head(正), false=tail(反)
let ichingData = null; // 动态加载的 64 卦基础库
let animationObserver = null; // 动画观察器

// DOM元素引用
let questionInput, clearQuestionBtn, suggestionsContainer;
let coinsContainer, startDivinationBtn;
let hexagramContainer, resultSection, detailedResultSection;
// AI分析相关元素
let aiResultSection, loadingIndicator, aiResultContent, regenerateBtn;

// 初始化
document.addEventListener('DOMContentLoaded', async function() {
    initTheme();
    initElements();
    initEventListeners();
    renderSuggestions();
    await loadIchingData();

    // 初始刷新统计UI（从localStorage读取）
    try {
        const key = 'divine_stats';
        const data = JSON.parse(localStorage.getItem(key) || '{}');
        const today = new Date().toISOString().slice(0, 10);
        updateStatsUI(data, today);
    } catch (e) {}

    // 避免硬币元素与 FLIP 竞争 transform（忽略这些元素的位移动画）
    try {
        document.querySelectorAll('.coin').forEach(function (el) {
            el.classList.add('ignore-animate');
        });
    } catch (e) {}
});

// 初始化DOM元素引用
function initElements() {
    questionInput = document.getElementById('question-input');
    clearQuestionBtn = document.getElementById('clear-question');
    suggestionsContainer = document.querySelector('.suggested-questions');
    coinsContainer = document.getElementById('coins-grid');
    startDivinationBtn = document.getElementById('start-divination');
    hexagramContainer = document.getElementById('hexagram');
    // 修正 ID：index.html 中为 id="result"
    resultSection = document.getElementById('result');
    detailedResultSection = document.getElementById('detailed-result');
    // AI相关元素
    aiResultSection = document.getElementById('ai-result-section');
    loadingIndicator = document.getElementById('loading-indicator');
    aiResultContent = document.getElementById('ai-result-content');
    regenerateBtn = document.getElementById('regenerate-btn');
}

// 更新进度显示
function updateProgress(roundOverride, label) {
    const roundInfo = document.getElementById('round-info');
    const progressInfo = document.getElementById('progress-info');
    const round = typeof roundOverride === 'number' ? roundOverride : hexagramList.length;
    const shown = Math.min(round, totalRounds);
    if (roundInfo) roundInfo.textContent = shown >= totalRounds ? '卦象完成' : `第 ${Math.max(shown, 1)} 爻`;
    if (progressInfo) progressInfo.textContent = `${shown}/${totalRounds}`;
    if (label) roundInfo.textContent = `${roundInfo.textContent.replace(/ .*/, '')} ${label}`.trim();
}

// 初始化事件监听器
function initEventListeners() {
    // 主题切换
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    
    // 问题输入
    questionInput.addEventListener('input', handleQuestionInput);
    clearQuestionBtn.addEventListener('click', clearQuestion);
    
    // 开始算卦
    startDivinationBtn.addEventListener('click', startDivination);

    // 重新生成AI分析，不重新摇卦
    if (typeof regenerateBtn !== 'undefined' && regenerateBtn) {
        regenerateBtn.addEventListener('click', () => {
            if (!hexagramResult) return;
            triggerAI(currentQuestion, hexagramResult.hexInfo, hexagramResult.rec);
        });
    }
}

// 主题切换
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// 问题输入处理
function handleQuestionInput() {
    currentQuestion = questionInput.value.trim();
    clearQuestionBtn.style.display = currentQuestion ? 'flex' : 'none';
}

function clearQuestion() {
    questionInput.value = '';
    currentQuestion = '';
    clearQuestionBtn.style.display = 'none';
    questionInput.focus();
}

function selectSuggestion(question) {
    questionInput.value = question;
    currentQuestion = question;
    clearQuestionBtn.style.display = 'flex';
}

// 渲染推荐问题
function renderSuggestions() {
    const suggestionBtns = suggestionsContainer.querySelectorAll('.suggestion-btn');
    suggestionBtns.forEach(btn => {
        const question = btn.getAttribute('data-question');
        btn.addEventListener('click', () => selectSuggestion(question));
    });
}

// 开始算卦（重构：严格一轮一 await，同步“摇一次-出一爻”节奏）
// 严格按照divination项目的方案：每次点击触发一次硬币动画，动画结束后更新状态
function startDivination() {
    const question = questionInput.value.trim();
    if (!question) {
        alert('心诚则灵，请先输入您的问题。');
        questionInput.focus();
        return;
    }

    if (isAnimating) {
        return;
    }
    
    if (hexagramList.length >= 6) {
        hexagramList = [];
        resetUIForNewDivination();
    }
    
    startSingleRound();
}

// 开始单轮硬币动画
function startSingleRound() {
    if (isAnimating) {
        return;
    }
    
    const newFaces = generateCoinResults();
    isAnimating = true;
    updateProgress(hexagramList.length + 1, '摇卦中...');
    
    // 开始硬币动画，动画结束后会调用onTransitionEnd
    animateCoinsWithCallback(newFaces, lastFaces, onTransitionEnd);
    lastFaces = newFaces;
}

// 硬币动画结束后的回调函数（类似divination项目的onTransitionEnd）
function onTransitionEnd() {
    isAnimating = false;
    
    // 计算正面数量
    let frontCount = lastFaces.reduce((acc, val) => (val ? acc + 1 : acc), 0);
    
    // 更新hexagramList状态（严格按照divination项目的方案）
    const newLine = {
        change: frontCount == 0 || frontCount == 3,
        yang: frontCount >= 2,
        separate: hexagramList.length == 2 // 第3爻后显示分隔符
    };
    
    hexagramList = [...hexagramList, newLine];
    renderHexagram();
    
    // 如果还没有6爻，自动继续下一轮（模拟AUTO_DELAY）
    if (hexagramList.length < 6) {
        setTimeout(() => {
            startSingleRound();
        }, 600); // AUTO_DELAY
    } else {
        // 6爻完成，显示结果
        updateProgress(6, '卦象完成');
        const fullResult = calculateHexagram(hexagramList);
        showResult(fullResult);
        startDivinationBtn.textContent = '重新卜筮';
    }
}

// 硬币动画：仅负责动画，不推进业务流程
async function animateCoins(newFaces, oldFaces) {
    const coins = coinsContainer.querySelectorAll('.coin');
    const tasks = Array.from(coins).map((coinEl, idx) => animateCoin(coinEl, newFaces[idx], oldFaces[idx]));
    await Promise.all(tasks);
}

// 带回调的硬币动画函数（严格按照divination项目的方案）
function animateCoinsWithCallback(newFaces, oldFaces, callback) {
    const coins = coinsContainer.querySelectorAll('.coin');
    const tasks = Array.from(coins).map((coinEl, idx) => animateCoin(coinEl, newFaces[idx], oldFaces[idx]));
    Promise.all(tasks).then(() => {
        if (callback) callback();
    });
}

function animateCoin(coinElement, resultFace, prevFace) {
    return new Promise((resolve) => {
        // 清理旧动画类
        coinElement.className = 'coin';
        // 选择动画类
        let animClass = '';
        if (prevFace && resultFace) animClass = 'anim-cff';
        else if (prevFace && !resultFace) animClass = 'anim-cfb';
        else if (!prevFace && resultFace) animClass = 'anim-bff';
        else animClass = 'anim-bfb';
        // 起始角度与动画
        coinElement.style.transform = prevFace ? 'rotateY(0deg)' : 'rotateY(180deg)';
        void coinElement.offsetWidth; // 强制重绘
        coinElement.classList.add(animClass);
        // 结束回调
        let done = false;
        const onAnimEnd = () => {
            if (done) return;
            done = true;
            coinElement.removeEventListener('animationend', onAnimEnd);
            coinElement.classList.remove(animClass);
            coinElement.style.transform = resultFace ? 'rotateY(0deg)' : 'rotateY(180deg)';
                resolve();
        };
        coinElement.addEventListener('animationend', onAnimEnd);
        // 容错：某些浏览器/首次渲染可能不触发 animationend，这里兜底
        setTimeout(onAnimEnd, 1400);
    });
}

// 生成随机硬币结果
function generateCoinResults() {
    // 仅三枚（一次一爻）
    return Array.from({ length: 3 }, () => Math.random() > 0.5);
}

// 由三枚硬币计算一爻的函数已被移除，现在直接在onTransitionEnd中计算

// 计算卦象
function calculateHexagram(lines) {
    if (!lines || lines.length !== 6) {
        return null;
    }

    // 计算上下卦索引（阳=1 阴=0；自下而上权重1、2、4）
    const lowerTrigram = (lines[0].yang ? 1 : 0) + (lines[1].yang ? 2 : 0) + (lines[2].yang ? 4 : 0);
    const upperTrigram = (lines[3].yang ? 1 : 0) + (lines[4].yang ? 2 : 0) + (lines[5].yang ? 4 : 0);

    const guaIndexValue = guaIndex[upperTrigram][lowerTrigram];
    const guaName = guaList[guaIndexValue];
    const sequence = guaIndexValue + 1;

    const YAO_NAMES_YANG = ["初九", "九二", "九三", "九四", "九五", "上九"]; // 阳动
    const YAO_NAMES_YIN  = ["初六", "六二", "六三", "六四", "六五", "上六"]; // 阴动
    const changeList = lines
        .map((line, i) => line.change ? (line.yang ? YAO_NAMES_YANG[i] : YAO_NAMES_YIN[i]) : null)
        .filter(Boolean);

    const GUA_DICTS = {
        names: ["坤", "震", "坎", "兑", "艮", "离", "巽", "乾"],
        symbols: ["地", "雷", "水", "泽", "山", "火", "风", "天"],
    };
    const upperSymbol = GUA_DICTS.symbols[upperTrigram];
    const lowerSymbol = GUA_DICTS.symbols[lowerTrigram];
    const upperName = GUA_DICTS.names[upperTrigram];
    const lowerName = GUA_DICTS.names[lowerTrigram];
    const fullGuaName = (upperTrigram === lowerTrigram)
        ? `${upperName}为${upperSymbol}`
        : `${upperSymbol}${lowerSymbol}${guaName}`;

    return {
        name: guaName,
        sequence,
        fullGuaName,
        positionDesc: `${upperName}上${lowerName}下`,
        changeList,
        change: changeList.length ? `变爻: ${changeList.join('、')}` : '无变爻',
        link: `https://zhouyi.sunls.de/${String(sequence).padStart(2, '0')}.${fullGuaName}/`,
    };
}

// 渲染卦象 - 状态驱动的完整渲染
function renderHexagram() {
    // 确保区域可见
    const hexSec = document.getElementById('hexagram-section');
    hexSec.style.display = 'block';
    hexSec.classList.add('show');

    // 增量渲染：只添加新的卦线
    if (hexagramList.length === 1) {
        // 第一条卦线，清空容器并初始化
        hexagramContainer.innerHTML = '';
        
        // 初始化动画观察器
        if (!animationObserver && hexagramContainer) {
            animationObserver = animateChildren(hexagramContainer);
        }
    }
    
    // 获取最新的卦线数据
    const latestIndex = hexagramList.length - 1;
    const latestLineData = hexagramList[latestIndex];
    
    // 创建新卦线行
    const newRow = createHexagramRow(latestLineData, latestIndex);
    
    // 由于要保持上六下初的顺序，新卦线应该添加到容器的末尾
    // 因为hexagramList是按初爻到上爻的顺序存储，最后渲染时需要反转显示
    hexagramContainer.appendChild(newRow);
    
    // 在第3爻后添加分隔线（只在第3爻时添加）
    if (latestLineData.separate) {
        const sep = document.createElement('div');
        sep.className = 'hex-sep';
        hexagramContainer.appendChild(sep);
    }
}

// 创建单个卦线行
function createHexagramRow(lineData, index) {
    const row = document.createElement('div');
    row.className = 'hexagram-row';
    row.setAttribute('data-line-index', index);

    const label = document.createElement('span');
    label.className = 'line-label';
    const YAO_NAMES_YANG = ["初九", "九二", "九三", "九四", "九五", "上九"]; 
    const YAO_NAMES_YIN  = ["初六", "六二", "六三", "六四", "六五", "上六"]; 
    // 由于渲染时已经反转了顺序，这里直接使用index即可
    label.textContent = lineData.yang ? YAO_NAMES_YANG[index] : YAO_NAMES_YIN[index];

    const visual = document.createElement('div');
    visual.className = 'line-visual';
    if (lineData.yang) {
        const part = document.createElement('div');
        part.className = `line-part yang ${lineData.change ? 'changing' : ''}`;
        visual.appendChild(part);
    } else {
        const p1 = document.createElement('div');
        const p2 = document.createElement('div');
        p1.className = `line-part yin ${lineData.change ? 'changing' : ''}`;
        p2.className = `line-part yin ${lineData.change ? 'changing' : ''}`;
        visual.appendChild(p1);
        visual.appendChild(p2);
    }

    const marker = document.createElement('span');
    marker.className = 'change-marker' + (lineData.yang ? '' : ' yin');
    if (lineData.change) marker.textContent = lineData.yang ? '○' : '✕';

    row.appendChild(label);
    row.appendChild(visual);
    row.appendChild(marker);
    
    return row;
}

// 用底部占位符替换为真实卦线，确保自下而上渐进
// renderSingleNewLine函数已被renderHexagram替代，不再需要

// 显示结果
function showResult(result) {
    if (!result) return;

    // 顶部横向卦象标题
    const headerEl = document.getElementById('hexagram-result-header');
    if (headerEl) {
        headerEl.innerHTML = `<a href="${result.link}" target="_blank" rel="noopener noreferrer"><span style="font-size: 1.25em;">${result.name}卦</span> (${result.fullGuaName}) <span style="color: hsl(var(--muted-foreground)); font-size: 0.9em;">${result.positionDesc}</span></a>`;
        setTimeout(() => headerEl.classList.add('show'), 100);
    }

    let rec = ichingData ? ichingData[String(result.sequence)] : null;
    // 兜底：按卦名匹配
    if (!rec && ichingData) {
        for (const k in ichingData) {
            if (Object.prototype.hasOwnProperty.call(ichingData, k)) {
                const r = ichingData[k];
                if (r && r.name === result.name) { rec = r; break; }
            }
        }
    }
    if (!rec) return;

    const titleEl = document.getElementById('result-title');
    const subTitleEl = document.getElementById('result-subtitle');
    const linkEl = document.getElementById('result-link');
    const judgeEl = document.getElementById('judgement-text');
    const imageEl = document.getElementById('image-text');
    const yaoEl = document.getElementById('yao-texts');

    if (titleEl) titleEl.textContent = `${rec.name}卦 (${result.sequence})`;
    if (subTitleEl) subTitleEl.textContent = result.change;
    if (linkEl) linkEl.href = result.link;
    if (judgeEl) judgeEl.textContent = rec.judgement || '暂无';
    if (imageEl) imageEl.textContent = rec.image || '暂无';
    if (yaoEl) {
        if (result.changeList.length) {
            const texts = result.changeList.map(label => {
                const head = label.slice(0, 2);
                return (rec.lines || []).find(l => l.startsWith(head)) || `${label}：暂无爻辞`;
            }).join('\n');
            yaoEl.textContent = texts;
        } else {
            yaoEl.textContent = '无变爻，可依卦辞、象辞为断。';
        }
    }

    // 填充详细信息
    populateHexagramDetails(rec);
    
    // 展开详细解读区
    if (typeof detailedResultSection !== 'undefined' && detailedResultSection) {
        detailedResultSection.style.display = 'block';
    }
    
    // 显示详细信息区域
    const hexagramDetailsEl = document.getElementById('hexagram-details');
    if (hexagramDetailsEl) {
        hexagramDetailsEl.style.display = 'block';
    }
    
    resultSection.style.display = 'block';
    setTimeout(() => resultSection.classList.add('show'), 100);

    // 保存结果并触发统计与AI分析
    hexagramResult = { hexInfo: result, rec };
    updateStats(result);
    triggerAI(currentQuestion, result, rec);
}

// 动态加载易经基础库
async function loadIchingData() {
    try {
        const res = await fetch('/static/iching_basic.json');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        ichingData = await res.json();
    } catch (e) {
        console.error('加载 iching_basic.json 失败：', e);
        ichingData = null;
    }
}

// 填充卦象详细信息
function populateHexagramDetails(hexagramData) {
    if (!hexagramData) return;
    
    // 基本信息
    const nameEl = document.getElementById('hexagram-name');
    const aliasesEl = document.getElementById('hexagram-aliases');
    
    if (nameEl) nameEl.textContent = hexagramData.name || '—';
    if (aliasesEl) {
        const aliases = hexagramData.alias || [];
        aliasesEl.textContent = aliases.length > 0 ? aliases.join('、') : '—';
    }
    
    // 五行属性
    const primaryElementEl = document.getElementById('primary-element');
    
    if (hexagramData.five_elements_enhanced && primaryElementEl) {
        primaryElementEl.textContent = hexagramData.five_elements_enhanced.primary || '—';
    }
    
    // 运势简要
    if (hexagramData.fortune) {
        const overallEl = document.getElementById('fortune-overall');
        const generalEl = document.getElementById('fortune-general');
        const adviceEl = document.getElementById('fortune-advice');
        
        if (overallEl) overallEl.textContent = hexagramData.fortune.overall || '—';
        if (generalEl) generalEl.textContent = hexagramData.fortune.general || '—';
        if (adviceEl) adviceEl.textContent = hexagramData.fortune.advice || '—';
    }
}



// 重置 UI / 状态（新一轮卜卦前）
function resetUIForNewDivination() {
    hexagramList = [];
    hexagramResult = null;
    coinResults = [];
    
    // 断开动画观察器
    if (animationObserver) {
        animationObserver.disconnect();
        animationObserver = null;
    }
    
    lastFaces = [true, true, true];
    startDivinationBtn.disabled = true;
    startDivinationBtn.textContent = '卜筮中...';
    resultSection.style.display = 'none';
    resultSection.classList.remove('show');
    if (detailedResultSection) detailedResultSection.style.display = 'none';
    
    // 隐藏详细信息区域
    const hexagramDetailsEl = document.getElementById('hexagram-details');
    if (hexagramDetailsEl) {
        hexagramDetailsEl.style.display = 'none';
    }

    // 清空卦象容器
    hexagramContainer.innerHTML = '';
    updateProgress(0);

    // 清理AI区域
    if (aiResultSection) aiResultSection.style.display = 'none';
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    if (aiResultContent) aiResultContent.innerHTML = '';
    if (regenerateBtn) regenerateBtn.style.display = 'none';
}

// ===================== 本地统计 =====================
function updateStats(result) {
    try {
        const key = 'divine_stats';
        const today = new Date();
        const dstr = today.toISOString().slice(0, 10);
        const data = JSON.parse(localStorage.getItem(key) || '{}');
        data.total = (data.total || 0) + 1;
        data.byDate = data.byDate || {};
        data.byDate[dstr] = (data.byDate[dstr] || 0) + 1;
        data.byHexagram = data.byHexagram || {};
        data.byHexagram[result.name] = (data.byHexagram[result.name] || 0) + 1;
        localStorage.setItem(key, JSON.stringify(data));
        updateStatsUI(data, dstr);
    } catch (e) {
        console.warn('统计更新失败：', e);
    }
}
function updateStatsUI(data, dstr) {
    try {
        const totalEl = document.getElementById('stats-total');
        const todayEl = document.getElementById('stats-today');
        const freqEl = document.getElementById('stats-frequent');
        if (totalEl) totalEl.textContent = String(data.total || 0);
        if (todayEl) todayEl.textContent = String((data.byDate || {})[dstr] || 0);
        if (freqEl) {
            const bx = data.byHexagram || {};
            let top = '—';
            let max = 0;
            for (const k in bx) {
                if (Object.prototype.hasOwnProperty.call(bx, k)) {
                    if (bx[k] > max) { max = bx[k]; top = `${k}（${bx[k]}次）`; }
                }
            }
            freqEl.textContent = top;
        }
    } catch (e) {}
}

// ===================== AI 接入 =====================
function setAISectionVisible(show) {
    if (!aiResultSection) return;
    aiResultSection.style.display = show ? 'block' : 'none';
    // 添加/移除 show 类来触发 CSS 动画
    if (show) {
        aiResultSection.classList.add('show');
    } else {
        aiResultSection.classList.remove('show');
    }
    if (loadingIndicator) loadingIndicator.style.display = show ? 'flex' : 'none';
    if (regenerateBtn) regenerateBtn.style.display = show ? 'none' : 'inline-flex';
}
function buildHexagramForAI(result, rec) {
    return {
        name: rec?.name || result.name,
        sequence: result.sequence,
        fullName: result.fullGuaName,
        judgement: rec?.judgement || '',
        image: rec?.image || '',
        lines: Array.isArray(rec?.lines) ? rec.lines : [],
        changeList: Array.isArray(result.changeList) ? result.changeList : [],
    };
}
const API_BASE = (location.port === '8001') ? '' : 'http://localhost:8001';
async function triggerAI(question, result, rec) {
    try {
        // 展示AI区域与加载状态
        setAISectionVisible(true);
        if (aiResultContent) aiResultContent.innerHTML = '';
        const payload = {
            question: (question || '').trim() || '综合运势',
            model: 'Qwen/QwQ-32B',
            hexagram: buildHexagramForAI(result, rec),
        };
        const resp = await fetch(`${API_BASE}/api/ai`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        renderAIResult(resp.ok, data);
    } catch (e) {
        renderAIResult(false, { detail: String(e || '网络错误') });
    }
}
function renderAIResult(ok, data) {
    if (!aiResultSection || !aiResultContent) return;
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    if (ok && data && data.content) {
        const text = String(data.content);
        // 使用 marked 库将 Markdown 转换为 HTML
        try {
            const htmlContent = marked.parse(text);
            aiResultContent.innerHTML = htmlContent;
            console.log('AI 内容已渲染 (Markdown):', text); // 调试日志
        } catch (error) {
            // 如果 Markdown 解析失败，回退到原始文本处理
            console.warn('Markdown 解析失败，使用纯文本模式:', error);
            const parts = text.split(/\n+/).filter(Boolean);
            aiResultContent.innerHTML = parts.map(p => `<p>${escapeHTML(p)}</p>`).join('');
            console.log('AI 内容已渲染 (纯文本):', text); // 调试日志
        }
    } else {
        const msg = data?.detail || 'AI分析失败，请稍后重试或配置密钥。';
        aiResultContent.innerHTML = `<p class="muted">${escapeHTML(String(msg))}</p>`;
        console.log('AI 错误信息:', msg); // 调试日志
    }
    if (regenerateBtn) regenerateBtn.style.display = 'inline-flex';
    // 确保 AI 区域可见
    setAISectionVisible(true);
}
function escapeHTML(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}