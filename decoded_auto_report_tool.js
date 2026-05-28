// Facebook Auto Report Tool - Deobfuscated
// Original: VM-based bytecode obfuscation (JScrambler-style)
// Author: Lê Hoàng Anh Kiệt (Telegram: @AKIOS999)
// Price: 100K VND (VIP licensed tool)

// === CẤU TRÚC MÃ HÓA GỐC ===
// 1. VM interpreter (vmN_cf2ba9) thực thi bytecode tùy chỉnh
// 2. Global state object (vmI_750bb6) proxy các browser globals
// 3. Bytecode mã hóa Base64 chứa string tables + opcodes
// 4. Toàn bộ logic được biên dịch thành bytecode
//
// VM chặn: document, window, Promise, setTimeout, XPathResult,
// console, MouseEvent, Math, clearInterval, Date, setInterval,
// parseInt, parseFloat, isNaN, alert, KeyboardEvent, Object, Event

// === ENTRY POINT ===
// (function initAutoReportTool() { ... })()

// === TẠO GIAO DIỆN ===
function createUI() {
    const menu = document.createElement('div');
    menu.id = 'autoReportMenu';
    menu.style = 'position:fixed; top:20px; right:20px; width:320px; background:#111111; border:2px solid #00ff00; padding:12px; color:#00ff00; font-family:monospace; z-index:999999;';

    menu.innerHTML = `
        <style>
            @keyframes rgbRainbow {
                0% { color: #ff0000; text-shadow: 0 0 5px #ff0000; }
                15% { color: #ff7f00; text-shadow: 0 0 5px #ff7f00; }
                30% { color: #ffff00; text-shadow: 0 0 5px #ffff00; }
                45% { color: #00ff00; text-shadow: 0 0 5px #00ff00; }
                60% { color: #0000ff; text-shadow: 0 0 5px #0000ff; }
                75% { color: #4b0082; text-shadow: 0 0 5px #4b0082; }
                90% { color: #9400d3; text-shadow: 0 0 5px #9400d3; }
                100% { color: #ff0000; text-shadow: 0 0 5px #ff0000; }
            }
            .text-rainbow-vip {
                animation: rgbRainbow 2.5s linear infinite;
                font-size: 16px;
            }
        </style>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-bottom: 1px solid #333; padding-bottom: 5px;">
            <h3 style="margin:0; color:yellow; font-size: 16px; text-transform: uppercase;">🛡️ Auto Report</h3>
            <button id="btnMinMax" style="background:none; border:1px solid #0f0; color:#0f0; cursor:pointer; font-weight:bold; padding: 2px 6px; font-family: monospace;">[-]</button>
        </div>

        <div style="color: #00e5ff; font-size: 11px; text-align: center; margin-bottom: 10px; font-weight: bold; border-bottom: 1px dashed #00ff00; padding-bottom: 10px; line-height: 1.6;">
            Tác giả: <span style="color: yellow; text-transform: uppercase;">Lê Hoàng Anh Kiệt</span><br>
            Telegram: <span style="color: #00ff88; font-size: 12px;">@AKIOS999</span><br>
            Tool bản quyền VIP giá <span style="background: red; color: white; padding: 1px 4px; border-radius: 3px; font-size: 12px;">100K</span><br>
            <span style="color: #ffaa00;">Vô Box liên hệ Tele để được bao Update!</span>
        </div>

        <div style="background:#222; text-align:center; padding:8px; margin-bottom:15px; font-weight:bold; border:1px solid #00e5ff;">
            Meta (Khung Top 1)
        </div>

        ⏱️ THỜI GIAN: <span id="timerVIP" class="text-rainbow-vip">00:00:00</span>

        <label style="font-size: 12px; font-weight: bold;">Độ trễ tốc độ nhấp nhả (ms):</label>
        <input type="number" id="inpSpeed" value="100" min="0" style="width:100%; margin-top:5px; margin-bottom:10px; background:#222; color:#0f0; border:1px solid #0f0; padding:8px; box-sizing: border-box; font-size: 13px; font-weight: bold;">

        <label style="font-size: 12px; font-weight: bold;">Số vòng chạy (Loops):</label>
        <input type="number" id="inpLoops" value="1" min="1" style="width:100%; margin-top:5px; margin-bottom:10px; background:#222; color:#0f0; border:1px solid #0f0; padding:8px; box-sizing: border-box; font-size: 13px; font-weight: bold;">

        <label style="font-size: 12px; font-weight: bold;">Nghỉ giữa các vòng (Phút):</label>
        <input type="number" id="inpDelayMinutes" value="0" min="0" step="0.1" placeholder="VD: 1 hoặc 0.5" style="width:100%; margin-top:5px; margin-bottom:15px; background:#222; color:#0f0; border:1px solid #0f0; padding:8px; box-sizing: border-box; font-size: 13px; font-weight: bold;">

        <div style="margin-bottom:10px; display:flex; align-items:center; gap:8px;">
            <input type="checkbox" id="chkAlarm" checked style="cursor:pointer; width:16px; height:16px; accent-color:#0f0;">
            <label for="chkAlarm" style="cursor:pointer; color:#00ff88; font-weight:bold; font-size:12px;">🔔 báo động khi acc die</label>
        </div>

        <div style="display:flex; justify-content:space-between; margin-bottom:10px; gap: 8px;">
            <button id="btnStartTool" style="flex:1; background:#008000; color:white; border:1px solid #00ff00; padding:10px; cursor:pointer; font-weight:bold; font-size: 13px;">▶ BẮT ĐẦU</button>
            <button id="btnStopTool" style="flex:1; background:#b30000; color:white; border:1px solid #ff0000; padding:10px; cursor:pointer; font-weight:bold; font-size: 13px;">⏹ DỪNG</button>
        </div>

        <div id="statusText" style="color:cyan; font-size:12px; text-align:center; padding-top: 8px; border-top: 1px dashed #0f0; font-weight: bold;">Trạng thái: Đang chờ lệnh...</div>
    `;

    document.body.appendChild(menu);
}

// === HỆ THỐNG ÂM THANH CẢNH BÁO ===
function playAlarmSound() {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();

    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.type = 'square';
    oscillator.frequency.value = 850;
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    oscillator.start();

    gainNode.gain.setValueAtTime(1.0, ctx.currentTime);
    gainNode.gain.setValueAtTime(0.0, ctx.currentTime + 0.2);
    oscillator.stop(ctx.currentTime + 0.3);
}

// === TÌM ELEMENT BẰNG XPATH ===
function findElementByXPath(xpath) {
    const result = document.evaluate(
        xpath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    );
    return result.singleNodeValue;
}

// === MÔ PHỎNG CLICK CHUỘT ===
function simulateClick(element) {
    const rect = element.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;

    element.scrollIntoView({ behavior: 'smooth', block: 'center' });

    element.dispatchEvent(new MouseEvent('mousedown', { view: window, bubbles: true, cancelable: true, clientX: x, clientY: y }));
    element.dispatchEvent(new MouseEvent('mousemove', { view: window, bubbles: true, cancelable: true, clientX: x, clientY: y }));
    element.dispatchEvent(new MouseEvent('mouseup', { view: window, bubbles: true, cancelable: true, clientX: x, clientY: y }));
    element.dispatchEvent(new MouseEvent('click', { view: window, bubbles: true, cancelable: true, clientX: x, clientY: y }));
}

// === TÌM KIẾM FUZZY ===
function findElementByFuzzyText(searchText) {
    const elements = document.querySelectorAll(
        "span, div[role='button'], div[role='menuitem'], div[role='radio']"
    );
    for (const el of elements) {
        const text = el.innerText.toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
        if (text.includes(searchText.toLowerCase().replace(/[^\p{L}\p{N}]/gu, ''))) {
            if (el.offsetParent !== null) {
                return el;
            }
        }
    }
    return null;
}

// === PHÁT HIỆN META/VIP ===
function findMetaInListbox() {
    const spans = document.querySelectorAll(
        'div[role="listbox"] span, ul[role="listbox"] span, div[role="presentation"] span'
    );
    for (const span of spans) {
        if (span.innerText.trim() === 'Meta') {
            console.log('--> [VIP] Đã tìm thấy chữ Meta! Click ngay!');
            return span;
        }
    }

    const imgs = document.querySelectorAll('div[role="listbox"] img');
    if (imgs.length > 0) {
        console.log('--> [VIP] Bị ẩn chữ, chuyển sang click vào hình ảnh Avatar đầu tiên!');
        return imgs[0];
    }

    return null;
}

// === QUY TRÌNH REPORT ===
// Bước 1: Click "Report profile"
// Bước 2: Chọn lý do (Something about this profile / Fake profile / ...)
// Bước 3: Click "Next"
// Bước 4: Dò tìm "Meta" (account VIP/verified)
// Bước 5: Điền URL nếu cần
// Bước 6: Click "Submit"
// Bước 7: Click "Done"
// Kiểm tra: "Thanks, we received your feedback" = thành công
//           "Sorry, something went wrong" = bị chặn

async function runAutoReport(settings) {
    const { speed, loops, delayMinutes, alarmEnabled } = settings;

    if (loops <= 0) {
        alert('Số vòng chạy phải lớn hơn 0!');
        return;
    }

    updateStatus('🚀 TOOL KHỞI ĐỘNG: Chạy ' + loops + ' vòng');

    for (let currentLoop = 0; currentLoop < loops; currentLoop++) {
        updateStatus('⚡ Đang chạy: Vòng ' + (currentLoop + 1) + '/' + loops);

        // Bước 1: Tìm nút Report profile
        let reportBtn = findElementByXPath("//span[normalize-space()='Report profile']");
        if (!reportBtn) {
            const threeDotsIcon = findElementByXPath(
                "//*[local-name()='svg' and *[local-name()='circle' and @cx='12'] and *[local-name()='circle' and @cx='19.5'] and *[local-name()='circle' and @cx='4.5']]"
            );
            if (threeDotsIcon) simulateClick(threeDotsIcon);
            await delay(speed);
            reportBtn = findElementByXPath("//span[normalize-space()='Report profile']");
        }

        if (!reportBtn) {
            updateStatus('❌ Lỗi: Mất nút ở Bước 1');
            break;
        }
        simulateClick(reportBtn);
        await delay(speed);

        // Bước 2: Chọn lý do report
        const reasons = [
            "//span[normalize-space()='Something about this profile']",
            "//span[normalize-space()='Fake profile']",
            "//span[normalize-space()='They\\'re not a real person']",
            "//span[normalize-space()='A celebrity or public figure']",
            "//span[normalize-space()='Credible threat to safety']",
            "//span[normalize-space()='Violent, hateful or disturbing content']",
            "//span[normalize-space()='Scam, fraud or false information']",
            "//span[normalize-space()='Fraud or scam']",
            "//span[normalize-space()='Spam']",
            "//span[normalize-space()='Physical abuse']",
            "//span[normalize-space()='Problem involving someone under 18']",
            "//span[normalize-space()='Something else']",
        ];

        let reasonFound = false;
        for (const xpath of reasons) {
            const el = findElementByXPath(xpath);
            if (el) {
                simulateClick(el);
                reasonFound = true;
                break;
            }
        }
        if (!reasonFound) {
            updateStatus('⚠️ Lệch chữ, đang dò Fuzzy...');
        }
        await delay(speed);

        // Bước 3: Click Next
        const nextBtn = findElementByXPath("//span[normalize-space()='Next']");
        if (nextBtn) simulateClick(nextBtn);
        await delay(speed);

        // Bước 4: Dò Meta/VIP
        updateStatus('⏳ Đang kích hoạt radar dò Meta...');
        await delay(speed);

        for (let retry = 0; retry < 5; retry++) {
            updateStatus('⏳ Đang tìm \'Meta\' trong danh sách... (Thử lại: ' + retry + ')');
            const metaEl = findMetaInListbox();
            if (metaEl) {
                simulateClick(metaEl);
                console.log('--> [FUZZY VIP] Đã bắt được mục tiêu: Meta');
                break;
            }
            await delay(speed);
        }

        // Bước 5: Điền URL nếu có input
        const pageUrlInput = findElementByXPath("//input[@aria-label='Facebook Page name or URL']");
        if (pageUrlInput) {
            simulateClick(pageUrlInput);
        }

        // Bước 6: Submit
        const submitBtn = findElementByXPath("//span[normalize-space()='Submit']");
        if (submitBtn) simulateClick(submitBtn);
        await delay(speed);

        // Bước 7: Done
        const doneBtn = findElementByXPath("//span[normalize-space()='Done']");
        if (doneBtn) simulateClick(doneBtn);
        await delay(speed);

        // Kiểm tra kết quả
        const pageText = document.body.innerText;
        if (pageText.includes('Thanks, we received your feedback')) {
            console.log('🎯 [RADAR] Đã hiện form: Thanks, we received your feedback!');
            updateStatus('✅ ĐÃ GHI NHẬN REPORT! TỰ ĐỘNG DỪNG!');
        } else if (pageText.includes('Sorry, something went wrong')) {
            console.log('🎯 [RADAR] Đã chộp được lỗi: Sorry, something went wrong!');
            updateStatus('❌ FB CHẶN (SOMETHING WENT WRONG)! ĐÃ DỪNG!');
            if (alarmEnabled) playAlarmSound();
            break;
        }

        // Nghỉ giữa các vòng
        if (delayMinutes > 0 && currentLoop < loops - 1) {
            const delaySec = delayMinutes * 60;
            for (let i = delaySec; i > 0; i--) {
                updateStatus('⏳ Đang nghỉ: Còn ' + i + ' giây...');
                await delay(1000);
            }
        }
    }

    updateStatus('✅ HOÀN THÀNH TOÀN BỘ!');
}

// === TIMER ===
let timerInterval = null;
let startTime = null;

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const h = Math.floor(elapsed / 3600).toString().padStart(2, '0');
        const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
        const s = (elapsed % 60).toString().padStart(2, '0');
        document.getElementById('timerVIP').innerText = h + ':' + m + ':' + s;
    }, 1000);
}

// === ĐIỀU KHIỂN ===
function setupControls() {
    document.getElementById('btnStartTool').onclick = () => {
        const speed = parseInt(document.getElementById('inpSpeed').value) || 100;
        const loops = parseInt(document.getElementById('inpLoops').value) || 1;
        const delayMinutes = parseFloat(document.getElementById('inpDelayMinutes').value) || 0;
        const alarmEnabled = document.getElementById('chkAlarm').checked;

        startTimer();
        runAutoReport({ speed, loops, delayMinutes, alarmEnabled });
    };

    document.getElementById('btnStopTool').onclick = () => {
        updateStatus('⚠️ Đang dừng luồng...');
        setTimeout(() => {
            updateStatus('🛑 Đã dừng theo lệnh!');
            if (timerInterval) clearInterval(timerInterval);
        }, 500);
    };

    document.getElementById('btnMinMax').onclick = () => {
        const menu = document.getElementById('autoReportMenu');
        menu.style.opacity = menu.style.opacity === '0' ? '1' : '0';
    };
}

// === HELPERS ===
function updateStatus(msg) {
    const el = document.getElementById('statusText');
    if (el) el.innerText = msg;
    console.log(msg);
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function simulateKeyPress(element, key) {
    const keyCode = key.charCodeAt(0);
    element.dispatchEvent(new KeyboardEvent('keydown', { key, code: key, keyCode, bubbles: true }));
    element.dispatchEvent(new KeyboardEvent('keypress', { key, code: key, keyCode, bubbles: true }));
    element.dispatchEvent(new KeyboardEvent('keyup', { key, code: key, keyCode, bubbles: true }));
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
}

// === KHỞI CHẠY ===
function initAutoReportTool() {
    createUI();
    setupControls();
}

initAutoReportTool();
