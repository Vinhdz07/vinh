// ==UserScript==
// @name         Auto Report Tool VIP
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Facebook Auto Report Tool - Meta/VIP
// @author       Lê Hoàng Anh Kiệt (@AKIOS999)
// @match        https://www.facebook.com/*
// @match        https://m.facebook.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    let timerInterval = null;
    let startTime = null;
    let isRunning = false;
    let shouldStop = false;

    // === TẠO GIAO DIỆN ===
    function createUI() {
        const menu = document.createElement('div');
        menu.id = 'autoReportMenu';
        menu.style.cssText = 'position:fixed; top:20px; right:20px; width:320px; background:#111111; border:2px solid #00ff00; padding:12px; color:#00ff00; font-family:monospace; z-index:999999; border-radius:8px; box-shadow: 0 0 20px rgba(0,255,0,0.3);';

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
                #autoReportMenu input[type="number"] {
                    width:100%; margin-top:5px; margin-bottom:10px;
                    background:#222; color:#0f0; border:1px solid #0f0;
                    padding:8px; box-sizing:border-box; font-size:13px;
                    font-weight:bold; border-radius:4px;
                }
                #autoReportMenu label {
                    font-size:12px; font-weight:bold; color:#0f0;
                }
                #autoReportMenu button {
                    cursor:pointer; font-weight:bold; border-radius:4px;
                }
            </style>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; border-bottom:1px solid #333; padding-bottom:5px;">
                <h3 style="margin:0; color:yellow; font-size:16px; text-transform:uppercase;">🛡️ Auto Report</h3>
                <button id="btnMinMax" style="background:none; border:1px solid #0f0; color:#0f0; padding:2px 6px; font-family:monospace;">[-]</button>
            </div>

            <div id="menuContent">
                <div style="color:#00e5ff; font-size:11px; text-align:center; margin-bottom:10px; font-weight:bold; border-bottom:1px dashed #00ff00; padding-bottom:10px; line-height:1.6;">
                    Tác giả: <span style="color:yellow; text-transform:uppercase;">Lê Hoàng Anh Kiệt</span><br>
                    Telegram: <span style="color:#00ff88; font-size:12px;">@AKIOS999</span><br>
                    Tool bản quyền VIP giá <span style="background:red; color:white; padding:1px 4px; border-radius:3px; font-size:12px;">100K</span><br>
                    <span style="color:#ffaa00;">Vô Box liên hệ Tele để được bao Update!</span>
                </div>

                <div style="background:#222; text-align:center; padding:8px; margin-bottom:15px; font-weight:bold; border:1px solid #00e5ff; border-radius:4px;">
                    Meta (Khung Top 1)
                </div>

                <div style="text-align:center; margin-bottom:10px;">
                    ⏱️ THỜI GIAN: <span id="timerVIP" class="text-rainbow-vip">00:00:00</span>
                </div>

                <label>Độ trễ tốc độ nhấp nhả (ms):</label>
                <input type="number" id="inpSpeed" value="100" min="0">

                <label>Số vòng chạy (Loops):</label>
                <input type="number" id="inpLoops" value="1" min="1">

                <label>Nghỉ giữa các vòng (Phút):</label>
                <input type="number" id="inpDelayMinutes" value="0" min="0" step="0.1" placeholder="VD: 1 hoặc 0.5" style="margin-bottom:15px!important;">

                <div style="margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                    <input type="checkbox" id="chkAlarm" checked style="cursor:pointer; width:16px; height:16px; accent-color:#0f0;">
                    <label for="chkAlarm" style="cursor:pointer; color:#00ff88;">🔔 Báo động khi acc die</label>
                </div>

                <div style="display:flex; justify-content:space-between; margin-bottom:10px; gap:8px;">
                    <button id="btnStartTool" style="flex:1; background:#008000; color:white; border:1px solid #00ff00; padding:10px; font-size:13px;">▶ BẮT ĐẦU</button>
                    <button id="btnStopTool" style="flex:1; background:#b30000; color:white; border:1px solid #ff0000; padding:10px; font-size:13px;">⏹ DỪNG</button>
                </div>

                <div id="statusText" style="color:cyan; font-size:12px; text-align:center; padding-top:8px; border-top:1px dashed #0f0; font-weight:bold;">Trạng thái: Đang chờ lệnh...</div>
            </div>
        `;

        document.body.appendChild(menu);
    }

    // === ÂM THANH CẢNH BÁO ===
    function playAlarmSound() {
        try {
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

            setTimeout(() => {
                oscillator.disconnect();
                gainNode.disconnect();
                ctx.close();
            }, 500);
        } catch(e) {
            console.log('Lỗi: Trình duyệt chặn phát âm thanh báo động!');
        }
    }

    // === TÌM ELEMENT BẰNG XPATH ===
    function findByXPath(xpath) {
        try {
            const result = document.evaluate(
                xpath, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null
            );
            return result.singleNodeValue;
        } catch(e) {
            return null;
        }
    }

    // === MÔ PHỎNG CLICK ===
    function simulateClick(element) {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        const events = ['mousedown', 'mousemove', 'mouseup', 'click'];
        events.forEach(type => {
            element.dispatchEvent(new MouseEvent(type, {
                view: window, bubbles: true, cancelable: true,
                clientX: x, clientY: y
            }));
        });
        return true;
    }

    // === MÔ PHỎNG GÕ PHÍM ===
    function simulateType(element, text) {
        element.focus();
        for (const char of text) {
            const keyCode = char.charCodeAt(0);
            ['keydown', 'keypress', 'keyup'].forEach(type => {
                element.dispatchEvent(new KeyboardEvent(type, {
                    key: char, code: char, keyCode, bubbles: true
                }));
            });
        }
        element.value = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // === TÌM KIẾM FUZZY ===
    function findByFuzzyText(searchText) {
        const selectors = "span, div[role='button'], div[role='menuitem'], div[role='radio']";
        const elements = document.querySelectorAll(selectors);
        const normalizedSearch = searchText.toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');

        for (const el of elements) {
            const text = el.innerText.toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
            if (text.includes(normalizedSearch) && el.offsetParent !== null) {
                return el;
            }
        }
        return null;
    }

    // === DÒ META/VIP ===
    function findMetaOption() {
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

    // === DELAY ===
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // === CẬP NHẬT TRẠNG THÁI ===
    function updateStatus(msg) {
        const el = document.getElementById('statusText');
        if (el) el.innerText = msg;
        console.log('[AutoReport] ' + msg);
    }

    // === TIMER ===
    function startTimer() {
        startTime = Date.now();
        timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const h = Math.floor(elapsed / 3600).toString().padStart(2, '0');
            const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
            const s = (elapsed % 60).toString().padStart(2, '0');
            const timerEl = document.getElementById('timerVIP');
            if (timerEl) timerEl.innerText = h + ':' + m + ':' + s;
        }, 1000);
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    // === LUỒNG REPORT CHÍNH ===
    async function runAutoReport(settings) {
        const { speed, loops, delayMinutes, alarmEnabled } = settings;

        if (loops <= 0) {
            alert('Số vòng chạy phải lớn hơn 0!');
            return;
        }

        isRunning = true;
        shouldStop = false;
        updateStatus('🚀 TOOL KHỞI ĐỘNG: Chạy ' + loops + ' vòng');

        for (let currentLoop = 0; currentLoop < loops; currentLoop++) {
            if (shouldStop) {
                updateStatus('🛑 Đã dừng theo lệnh!');
                break;
            }

            updateStatus('⚡ Đang chạy: Vòng ' + (currentLoop + 1) + '/' + loops);

            // === BƯỚC 1: Tìm nút Report profile ===
            let reportBtn = findByXPath("//span[normalize-space()='Report profile']");
            if (!reportBtn) {
                // Thử mở menu 3 chấm trước
                const threeDotsIcon = findByXPath(
                    "//*[local-name()='svg' and *[local-name()='circle' and @cx='12'] and *[local-name()='circle' and @cx='19.5'] and *[local-name()='circle' and @cx='4.5']]"
                );
                if (threeDotsIcon) simulateClick(threeDotsIcon);
                await delay(speed + 500);
                reportBtn = findByXPath("//span[normalize-space()='Report profile']");
            }

            if (!reportBtn) {
                updateStatus('❌ Lỗi: Mất nút ở Bước 1 - Không tìm thấy "Report profile"');
                break;
            }
            simulateClick(reportBtn);
            await delay(speed + 300);

            if (shouldStop) break;

            // === BƯỚC 2: Chọn lý do report ===
            const reasons = [
                "//span[normalize-space()='Something about this profile']",
                "//span[normalize-space()='Fake profile']",
                "//span[normalize-space()=\"They're not a real person\"]",
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
                const el = findByXPath(xpath);
                if (el) {
                    simulateClick(el);
                    reasonFound = true;
                    console.log('[AutoReport] Đã chọn lý do: ' + el.innerText);
                    break;
                }
            }

            if (!reasonFound) {
                updateStatus('⚠️ Lệch chữ, đang dò Fuzzy...');
                const fuzzyTargets = ['fake profile', 'spam', 'scam', 'something else'];
                for (const target of fuzzyTargets) {
                    const el = findByFuzzyText(target);
                    if (el) {
                        simulateClick(el);
                        reasonFound = true;
                        break;
                    }
                }
            }
            await delay(speed + 200);

            if (shouldStop) break;

            // === BƯỚC 3: Click Next ===
            const nextBtn = findByXPath("//span[normalize-space()='Next']");
            if (nextBtn) simulateClick(nextBtn);
            await delay(speed + 300);

            if (shouldStop) break;

            // === BƯỚC 4: Radar dò Meta/VIP ===
            updateStatus('⏳ Đang kích hoạt radar dò Meta...');
            let metaFound = false;

            for (let retry = 0; retry < 5; retry++) {
                if (shouldStop) break;
                updateStatus('⏳ Đang tìm \'Meta\' trong danh sách... (Thử lại: ' + (retry + 1) + ')');
                const metaEl = findMetaOption();
                if (metaEl) {
                    simulateClick(metaEl);
                    metaFound = true;
                    console.log('--> [FUZZY VIP] Đã bắt được mục tiêu: Meta');
                    break;
                }
                await delay(speed + 200);
            }
            await delay(speed);

            if (shouldStop) break;

            // === BƯỚC 5: Điền URL nếu có ===
            const pageUrlInput = findByXPath("//input[@aria-label='Facebook Page name or URL']");
            if (pageUrlInput) {
                simulateClick(pageUrlInput);
                await delay(200);
            }

            // === BƯỚC 6: Submit ===
            const submitBtn = findByXPath("//span[normalize-space()='Submit']");
            if (submitBtn) simulateClick(submitBtn);
            await delay(speed + 500);

            if (shouldStop) break;

            // === BƯỚC 7: Done ===
            const doneBtn = findByXPath("//span[normalize-space()='Done']");
            if (doneBtn) simulateClick(doneBtn);
            await delay(speed + 300);

            // === KIỂM TRA KẾT QUẢ ===
            await delay(500);
            const pageText = document.body.innerText || '';

            if (pageText.includes('Thanks, we received your feedback')) {
                console.log('🎯 [RADAR] Đã hiện form: Thanks, we received your feedback!');
                updateStatus('✅ ĐÃ GHI NHẬN REPORT! Vòng ' + (currentLoop + 1) + ' thành công!');
            } else if (pageText.includes('Sorry, something went wrong')) {
                console.log('🎯 [RADAR] Đã chộp được lỗi: Sorry, something went wrong!');
                updateStatus('❌ FB CHẶN (SOMETHING WENT WRONG)! ĐÃ DỪNG!');
                if (alarmEnabled) playAlarmSound();
                break;
            }

            // === NGHỈ GIỮA CÁC VÒNG ===
            if (delayMinutes > 0 && currentLoop < loops - 1) {
                const totalSec = Math.ceil(delayMinutes * 60);
                for (let i = totalSec; i > 0; i--) {
                    if (shouldStop) break;
                    updateStatus('⏳ Đang nghỉ: Còn ' + i + ' giây... (' + (currentLoop + 1) + '/' + loops + ' vòng)');
                    await delay(1000);
                }
            }
        }

        if (!shouldStop) {
            updateStatus('✅ HOÀN THÀNH TOÀN BỘ! (' + loops + ' vòng)');
        }
        isRunning = false;
        stopTimer();
    }

    // === GẮN SỰ KIỆN ===
    function setupControls() {
        document.getElementById('btnStartTool').onclick = () => {
            if (isRunning) {
                updateStatus('⚠️ Tool đang chạy rồi!');
                return;
            }
            const speed = parseInt(document.getElementById('inpSpeed').value) || 100;
            const loops = parseInt(document.getElementById('inpLoops').value) || 1;
            const delayMinutes = parseFloat(document.getElementById('inpDelayMinutes').value) || 0;
            const alarmEnabled = document.getElementById('chkAlarm').checked;

            startTimer();
            runAutoReport({ speed, loops, delayMinutes, alarmEnabled });
        };

        document.getElementById('btnStopTool').onclick = () => {
            if (!isRunning) return;
            shouldStop = true;
            updateStatus('⚠️ Đang dừng luồng...');
            setTimeout(() => {
                updateStatus('🛑 Đã dừng theo lệnh!');
                isRunning = false;
                stopTimer();
            }, 1000);
        };

        document.getElementById('btnMinMax').onclick = () => {
            const content = document.getElementById('menuContent');
            const btn = document.getElementById('btnMinMax');
            if (content.style.display === 'none') {
                content.style.display = 'block';
                btn.innerText = '[-]';
            } else {
                content.style.display = 'none';
                btn.innerText = '[+]';
            }
        };
    }

    // === KHỞI CHẠY ===
    function init() {
        if (document.getElementById('autoReportMenu')) return;
        createUI();
        setupControls();
        console.log('🛡️ Auto Report Tool loaded!');
    }

    if (document.readyState === 'complete') {
        init();
    } else {
        window.addEventListener('load', init);
    }

})();
