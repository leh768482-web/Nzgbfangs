import os
import re
import ipaddress
from urllib.parse import urlsplit, urlunsplit

import phonenumbers
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024

HTTP = requests.Session()
HTTP.headers.update({"User-Agent": "KiemTraAnToan/1.0"})
HTTP_TIMEOUT = 3.5

PAGE = r'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b1020">
<title>Kiểm Tra An Toàn</title>
<style>
:root{color-scheme:dark;--bg:#080d19;--panel:#10182b;--panel2:#141f35;--line:#263550;--text:#edf3ff;--muted:#9eacc5;--cyan:#66e0d4;--blue:#7ca6ff;--red:#ff777f;--yellow:#ffd479;--green:#7ce0a0}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 10% 0%,#172748 0,transparent 40%),radial-gradient(ellipse at 95% 15%,#123e46 0,transparent 30%),var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh}
main{width:min(920px,100%);margin:auto;padding:24px 16px 36px}.hero{padding:22px 4px 24px}.eyebrow{color:var(--cyan);font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase}.hero h1{font-size:clamp(30px,7vw,50px);line-height:1.05;letter-spacing:-.04em;margin:12px 0}.hero p{color:var(--muted);max-width:680px;margin:0;font-size:15px}.shield{display:inline-grid;place-items:center;width:46px;height:46px;border:1px solid #365b71;border-radius:15px;background:#102b38;font-size:24px;margin-bottom:12px}
.card{background:linear-gradient(150deg,rgba(20,31,53,.97),rgba(13,21,37,.97));border:1px solid var(--line);border-radius:22px;padding:20px;box-shadow:0 18px 55px #0003}.types{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-bottom:20px}.type{background:#0c1424;border:1px solid var(--line);border-radius:14px;padding:12px 8px;color:var(--muted);font:inherit;font-size:13px;cursor:pointer;min-height:70px}.type span{display:block;font-size:21px;margin-bottom:4px}.type[aria-pressed="true"]{background:#10343a;border-color:#4ccbc2;color:#edfffc;box-shadow:inset 0 0 0 1px #4ccbc255}
label{display:block;color:#dce6f9;font-size:14px;font-weight:700;margin-bottom:8px}.entry{display:flex;gap:9px}.entry input{min-width:0;flex:1;background:#080f1e;color:var(--text);border:1px solid #31415f;border-radius:13px;padding:15px 14px;font:inherit;outline:none}.entry input:focus{border-color:var(--cyan);box-shadow:0 0 0 3px #66e0d422}.entry button{border:0;border-radius:13px;padding:0 19px;color:#061818;background:linear-gradient(135deg,var(--cyan),#76b9ff);font:inherit;font-weight:850;cursor:pointer}.entry button:disabled{opacity:.6;cursor:wait}.hint{font-size:12px;color:var(--muted);margin:9px 0 0}.examples{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px;align-items:center}.examples b{font-size:12px;color:var(--muted);font-weight:600}.chip{border:1px solid #2b3a53;background:#101b2e;color:#d6e4ff;border-radius:100px;padding:7px 10px;font-size:12px;cursor:pointer}.result{display:none;margin-top:16px;border:1px solid var(--line);background:#0b1322;border-radius:18px;padding:18px}.result.show{display:block}.result-head{display:flex;gap:12px;align-items:flex-start}.result-icon{display:grid;place-items:center;width:40px;height:40px;border-radius:13px;background:#19273b;font-size:20px;flex-shrink:0}.result h2{font-size:19px;margin:0 0 4px}.result p{color:var(--muted);margin:0;font-size:14px}.result ul{margin:16px 0 0;padding-left:20px;color:#d7e1f4;font-size:14px}.result li{margin:7px 0}.safe .result-icon{background:#11352a}.danger .result-icon{background:#3b1c29}.warn .result-icon{background:#392f1a}.neutral .result-icon{background:#182a41}.footnote{margin-top:18px;padding:15px 16px;border-left:3px solid #d8ae5a;background:#171a22;border-radius:0 12px 12px 0;color:#d8d6ce;font-size:13px}.footer{color:#71819e;font-size:12px;text-align:center;margin:18px 0 0}.spinner{display:inline-block;width:14px;height:14px;border:2px solid #163d43;border-top-color:transparent;border-radius:50%;animation:spin .7s linear infinite;vertical-align:-2px;margin-right:7px}@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:520px){main{padding:17px 12px 28px}.hero{padding:17px 4px 20px}.card{padding:14px;border-radius:18px}.types{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.type{min-height:62px;padding:9px}.entry{flex-direction:column}.entry button{min-height:48px}.result{padding:14px}}
</style>
</head>
<body><main>
<section class="hero"><div class="shield">🛡️</div><div class="eyebrow">BỘ KIỂM TRA THÔNG TIN</div><h1>Kiểm tra trước<br>khi tin tưởng.</h1><p>Kiểm tra dấu hiệu giả mạo của số điện thoại, Gmail, ID TikTok và đường dẫn web. Kết quả nói rõ điều gì kiểm tra được và điều gì chưa thể xác minh.</p></section>
<section class="card">
<div class="types" role="group" aria-label="Chọn loại cần kiểm tra">
<button class="type" data-type="phone" aria-pressed="true"><span>📱</span>Số điện thoại</button>
<button class="type" data-type="gmail" aria-pressed="false"><span>✉️</span>Gmail</button>
<button class="type" data-type="tiktok" aria-pressed="false"><span>🎵</span>ID TikTok</button>
<button class="type" data-type="url" aria-pressed="false"><span>🔗</span>Liên kết web</button>
</div>
<form id="checker"><label id="inputLabel" for="value">Nhập số điện thoại cần kiểm tra</label><div class="entry"><input id="value" name="value" maxlength="2048" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Ví dụ: 012345678" required><button id="submit" type="submit">Kiểm tra ↗</button></div><p id="hint" class="hint">Dùng số Việt Nam hoặc số quốc tế có mã quốc gia, ví dụ +84…</p></form>
<div class="examples"><b>Thử ví dụ:</b><button class="chip" data-example="012345678" data-kind="phone">012345678 (không hợp lệ)</button><button class="chip" data-example="test@gmail.com" data-kind="gmail">test@gmail.com</button><button class="chip" data-example="@username" data-kind="tiktok">@username</button><button class="chip" data-example="http://example.com" data-kind="url">http://example.com</button></div>
<div id="result" class="result" aria-live="polite"></div>
</section>
<div class="footnote"><b>Lưu ý quan trọng:</b> Định dạng đúng không chứng minh tài khoản tồn tại hoặc đang hoạt động. Với đường link, không phát hiện cảnh báo cũng không đồng nghĩa an toàn tuyệt đối. Không nhập mật khẩu, mã OTP hay thông tin riêng tư vào công cụ này.</div>
<div class="footer">Không lưu lịch sử kiểm tra trên máy chủ ứng dụng. Kết quả chỉ mang tính tham khảo.</div>
</main>
<script>
const configs={
 phone:{label:'Nhập số điện thoại cần kiểm tra',placeholder:'Ví dụ: 012345678',hint:'Dùng số Việt Nam hoặc số quốc tế có mã quốc gia, ví dụ +84…',button:'Kiểm tra số'},
 gmail:{label:'Nhập địa chỉ Gmail',placeholder:'tenban@gmail.com',hint:'Kiểm tra định dạng và các dấu hiệu địa chỉ mẫu; không xác minh hộp thư bằng cách gửi email.',button:'Kiểm tra Gmail'},
 tiktok:{label:'Nhập ID TikTok',placeholder:'@ten_tai_khoan',hint:'Nhập username hoặc @username, không cần dán liên kết hồ sơ.',button:'Kiểm tra ID'},
 url:{label:'Dán liên kết web cần kiểm tra',placeholder:'https://example.com',hint:'Có thể dán đường link đầy đủ. Nếu có Google Safe Browsing API key, app sẽ kiểm tra thêm danh sách cảnh báo.',button:'Quét liên kết'}
};
let kind='phone';const input=document.querySelector('#value'),result=document.querySelector('#result'),submit=document.querySelector('#submit');
function choose(k){kind=k;document.querySelectorAll('.type').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.type===k)));document.querySelector('#inputLabel').textContent=configs[k].label;input.placeholder=configs[k].placeholder;document.querySelector('#hint').textContent=configs[k].hint;submit.textContent=configs[k].button;input.value='';result.className='result';result.innerHTML='';input.focus()}
document.querySelectorAll('.type').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.type)));
document.querySelectorAll('.chip').forEach(b=>b.addEventListener('click',()=>{choose(b.dataset.kind);input.value=b.dataset.example;input.focus()}));
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function paint(d){const styles={danger:['danger','⚠️'],warn:['warn','🟡'],safe:['safe','✅'],neutral:['neutral','🔎']};const [cl,ico]=styles[d.level]||styles.neutral;result.className='result show '+cl;result.innerHTML=`<div class="result-head"><div class="result-icon">${ico}</div><div><h2>${esc(d.title)}</h2><p>${esc(d.summary)}</p></div></div><ul>${(d.details||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`}
document.querySelector('#checker').addEventListener('submit',async e=>{e.preventDefault();const value=input.value.trim();if(!value)return;submit.disabled=true;submit.innerHTML='<span class="spinner"></span>Đang kiểm tra';result.className='result show neutral';result.innerHTML='<p>Đang phân tích thông tin…</p>';try{const r=await fetch('/api/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:kind,value})});const d=await r.json();if(!r.ok)throw new Error(d.error||'Không thể kiểm tra dữ liệu.');paint(d)}catch(err){paint({level:'danger',title:'Không kiểm tra được',summary:err.message||'Có lỗi kết nối.',details:['Thử lại với giá trị khác.']})}finally{submit.disabled=false;submit.textContent=configs[kind].button}});
</script></body></html>'''


def result(level, title, summary, details):
    return {"level": level, "title": title, "summary": summary, "details": details}


def looks_like_placeholder_digits(digits):
    # Only flag a whole repeated/sequential string; do not reject a normal phone
    # number merely because a few consecutive digits appear somewhere inside it.
    if not digits or not digits.isdigit():
        return False
    variants = [digits]
    # Accommodate a Vietnamese country code added before a placeholder number.
    if digits.startswith("0084"):
        variants.append(digits[4:])
    if digits.startswith("84"):
        variants.append(digits[2:])
    seq = "0123456789"
    rev = seq[::-1]
    for candidate in variants:
        if len(candidate) >= 7 and len(set(candidate)) == 1:
            return True
        if 7 <= len(candidate) <= 10 and (candidate == seq[:len(candidate)] or candidate == rev[-len(candidate):]):
            return True
    return False


def check_phone(raw):
    original = raw.strip()
    digits = re.sub(r"\D", "", original)
    if not original or len(original) > 40:
        return result("danger", "Số điện thoại không hợp lệ", "Không thể xử lý giá trị đã nhập.", ["Kiểm tra lại số và thử nhập mã quốc gia nếu là số quốc tế."])
    if looks_like_placeholder_digits(digits):
        return result("danger", "Có dấu hiệu là số mẫu/giả", f"{original} chứa chuỗi chữ số lặp hoặc tăng/giảm liên tiếp thường được dùng làm ví dụ.", ["012345678 là số quá ngắn và không hợp lệ theo kế hoạch đánh số Việt Nam.", "Đây là kết luận về mẫu/định dạng, không phải truy vấn danh tính người sử dụng."])
    try:
        parsed = phonenumbers.parse(original, "VN")
    except phonenumbers.NumberParseException:
        return result("danger", "Không đúng định dạng số điện thoại", "Không thể phân tích số này theo quy tắc số điện thoại Việt Nam/quốc tế.", ["Nếu là số quốc tế, hãy nhập kèm mã quốc gia, ví dụ +84…", "Định dạng sai không cho phép kết luận ai sở hữu số đó."])
    if not phonenumbers.is_possible_number(parsed):
        return result("danger", "Số điện thoại không hợp lệ", "Độ dài hoặc cấu trúc số không phù hợp với kế hoạch đánh số của quốc gia được suy ra.", ["Hãy kiểm tra lại từng chữ số và mã quốc gia.", "Một số hợp lệ về cấu trúc vẫn có thể chưa được cấp phát hoặc đã ngừng hoạt động."])
    region = phonenumbers.region_code_for_number(parsed) or "không xác định"
    formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    if not phonenumbers.is_valid_number(parsed):
        return result("warn", "Độ dài có vẻ hợp lý nhưng dải số chưa hợp lệ", f"Số chuẩn hóa: {formatted} · Quốc gia/vùng: {region}.", ["Dải đầu số không khớp metadata hiện có hoặc không được nhận diện là số hợp lệ.", "Không thể xác minh số có đang hoạt động, có người sử dụng hay không chỉ từ chuỗi số."])
    return result("safe", "Cấu trúc số điện thoại hợp lệ", f"Số chuẩn hóa: {formatted} · Quốc gia/vùng: {region}.", ["Số này phù hợp với quy tắc đánh số đã biết.", "Không đồng nghĩa số đang hoạt động, có thể gọi được, hay xác định được chủ thuê bao."])


GMAIL_PLACEHOLDERS = {"test", "fake", "example", "yourname", "username", "name", "email", "sample", "abc", "admin"}


def check_gmail(raw):
    value = raw.strip()
    if len(value) > 320 or "@" not in value:
        return result("danger", "Địa chỉ không hợp lệ", "Hãy nhập một địa chỉ Gmail đầy đủ, ví dụ tenban@gmail.com.", ["Công cụ này kiểm tra Gmail (@gmail.com), không phải mọi loại email."])
    if value.count("@") != 1:
        return result("danger", "Địa chỉ không hợp lệ", "Địa chỉ phải có một ký tự @.", ["Kiểm tra lại phần tên người dùng và tên miền."])
    local, domain = value.rsplit("@", 1)
    if domain.lower() != "gmail.com":
        return result("danger", "Không phải địa chỉ Gmail", "Tên miền cần kết thúc đúng bằng @gmail.com.", ["Tên miền gần giống Gmail có thể là giả mạo; đừng đăng nhập qua liên kết lạ."])
    base = local.split("+", 1)[0]
    valid_base = (1 <= len(base) <= 30 and re.fullmatch(r"[A-Za-z0-9.]+", base) is not None
                  and not base.startswith(".") and not base.endswith(".") and ".." not in base)
    alias_ok = ("+" not in local or (local.count("+") == 1 and bool(local.split("+", 1)[1])
                and re.fullmatch(r"[A-Za-z0-9._-]+", local.split("+", 1)[1]) is not None))
    if not valid_base or not alias_ok:
        return result("danger", "Định dạng Gmail không hợp lệ", "Tên người dùng chứa ký tự hoặc cách viết không được hỗ trợ theo quy tắc cơ bản của Gmail.", ["Kiểm tra dấu chấm, dấu cộng và ký tự trong địa chỉ."])
    details = ["Định dạng địa chỉ phù hợp với dạng Gmail cơ bản.", "Không thể xác nhận hộp thư có tồn tại, còn hoạt động hay thuộc về một người cụ thể nếu không có xác minh từ nhà cung cấp."]
    if base.lower() in GMAIL_PLACEHOLDERS or (base.isdigit() and looks_like_placeholder_digits(base)):
        return result("warn", "Địa chỉ đúng dạng nhưng có vẻ là tên mẫu", f"Đã nhận diện địa chỉ: {value}.", ["Tên như test/example/username thường được dùng làm dữ liệu minh họa, nhưng bản thân tên đó không chứng minh hộp thư giả.", *details])
    return result("safe", "Định dạng Gmail có vẻ hợp lệ", f"Đã nhận diện địa chỉ: {value}.", details)


TIKTOK_PLACEHOLDERS = {"test", "fake", "example", "username", "yourname", "tiktok", "abc", "abcdef"}


def check_tiktok(raw):
    value = raw.strip()
    username = value[1:] if value.startswith("@") else value
    if not username or len(username) > 24 or not re.fullmatch(r"[A-Za-z0-9._]+", username) or username.endswith("."):
        return result("danger", "ID TikTok không đúng định dạng cơ bản", "Tên người dùng chỉ nên chứa chữ cái, chữ số, dấu chấm hoặc gạch dưới và tối đa 24 ký tự.", ["Nhập username, có hoặc không có ký tự @.", "Định dạng sai không giúp xác định ai đứng sau tài khoản."])
    if len(username) < 2:
        return result("danger", "ID TikTok quá ngắn", "Tên người dùng cần ít nhất 2 ký tự theo quy tắc kiểm tra của công cụ.", ["Kiểm tra lại ID."])
    if username.lower() in TIKTOK_PLACEHOLDERS or looks_like_placeholder_digits(username) and username.isdigit():
        return result("warn", "ID đúng dạng nhưng có vẻ là tên mẫu", f"ID được nhập: @{username}.", ["Tên như username/test/abcdef thường dùng làm ví dụ; điều đó không chứng minh chắc chắn tài khoản không tồn tại.", "App không đăng nhập vào TikTok và không thể xác nhận tài khoản đang hoạt động."])
    return result("safe", "ID phù hợp định dạng cơ bản", f"Hồ sơ dự kiến: https://www.tiktok.com/@{username}", ["Công cụ chỉ kiểm tra cú pháp của ID; hiện chưa xác minh được tài khoản có thật, đang hoạt động hay thuộc về ai.", "Để xác minh, hãy mở hồ sơ trong ứng dụng TikTok chính thức và kiểm tra trực tiếp."])


SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy", "shorturl.at", "ow.ly", "buff.ly", "soo.gd"}
BRANDS = {
    "paypal": {"paypal.com"}, "google": {"google.com", "google.com.vn"},
    "facebook": {"facebook.com", "fb.com"}, "microsoft": {"microsoft.com", "live.com", "outlook.com"},
    "apple": {"apple.com"}, "tiktok": {"tiktok.com"}, "instagram": {"instagram.com"},
}
URL_WORDS = {"login", "signin", "verify", "password", "wallet", "claim", "bonus", "airdrop", "gift", "account", "update"}


def dns_exists(host):
    """Use DNS-over-HTTPS; return True/False/None if the check could not be performed."""
    try:
        saw_nxdomain = False
        for record_type in ("A", "AAAA"):
            r = HTTP.get("https://dns.google/resolve", params={"name": host, "type": record_type}, timeout=HTTP_TIMEOUT,
                         headers={"Accept": "application/dns-json"})
            if r.status_code != 200:
                return None
            payload = r.json()
            status = payload.get("Status")
            if status == 0 and payload.get("Answer"):
                return True
            if status == 3:
                saw_nxdomain = True
        return False if saw_nxdomain else None
    except (requests.RequestException, ValueError):
        return None


def google_safe_browsing(url):
    key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()
    if not key:
        return None, "Chưa bật kiểm tra Google Safe Browsing (chưa cấu hình API key)."
    endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    body = {
        "client": {"clientId": "kiem-tra-an-toan-render", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        r = HTTP.post(endpoint, params={"key": key}, json=body, timeout=HTTP_TIMEOUT)
        if r.status_code != 200:
            return None, "Google Safe Browsing không trả về kết quả xác minh được; kiểm tra khóa API/quota nếu đã cấu hình."
        payload = r.json()
        matches = payload.get("matches") or []
        if matches:
            threat = sorted({m.get("threatType", "mối đe dọa") for m in matches})
            return True, "Google Safe Browsing báo khớp danh sách cảnh báo: " + ", ".join(threat) + "."
        return False, "Không có kết quả khớp trong danh sách Google Safe Browsing ở thời điểm kiểm tra; điều này không bảo đảm an toàn tuyệt đối."
    except (requests.RequestException, ValueError):
        return None, "Không kết nối được Google Safe Browsing để xác minh danh tiếng đường dẫn."


def check_url(raw):
    value = raw.strip()
    if not value or len(value) > 2048:
        return result("danger", "Liên kết trống hoặc quá dài", "Hãy dán một URL ngắn hơn 2048 ký tự.", ["Chỉ hỗ trợ liên kết web http:// hoặc https://."])
    if any(ord(c) < 32 for c in value) or "\\" in value:
        return result("danger", "Liên kết có ký tự bất thường", "URL chứa ký tự điều khiển hoặc dấu gạch chéo ngược.", ["Không mở liên kết được biến đổi hoặc không rõ nguồn."])
    candidate = value if re.match(r"^https?://", value, re.I) else "https://" + value
    try:
        parts = urlsplit(candidate)
        host_raw = parts.hostname
        port = parts.port  # also validates malformed ports
    except ValueError:
        return result("danger", "URL không hợp lệ", "Không thể phân tích địa chỉ web.", ["Kiểm tra chính tả đường link."])
    if parts.scheme.lower() not in {"http", "https"} or not host_raw:
        return result("danger", "URL không được hỗ trợ", "Chỉ chấp nhận liên kết HTTP hoặc HTTPS có tên máy chủ.", ["Không mở các địa chỉ như javascript:, data: hoặc file:."])
    if parts.username is not None or parts.password is not None:
        return result("danger", "Liên kết có thông tin đăng nhập nhúng", "URL có phần tên người dùng/mật khẩu trước tên miền — đây là cách có thể dùng để đánh lừa người xem.", ["Không nhập thông tin đăng nhập qua một liên kết có dạng bất thường."])
    try:
        host = host_raw.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        return result("danger", "Tên miền không hợp lệ", "Không thể chuẩn hóa tên miền.", ["Kiểm tra lại liên kết."])
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return result("danger", "Địa chỉ nội bộ, không phải website công khai", f"Tên máy chủ: {host}.", ["Địa chỉ cục bộ không thể được xác minh như một website công khai."])
    try:
        ip = ipaddress.ip_address(host.strip("[]"))
        if not ip.is_global:
            return result("danger", "Địa chỉ IP không công khai", f"Máy chủ dùng IP riêng/đặc biệt: {host}.", ["Không mở liên kết trỏ đến mạng nội bộ hoặc địa chỉ IP không định tuyến công khai."])
        ip_literal = True
    except ValueError:
        ip_literal = False
    if not ip_literal and "." not in host:
        return result("danger", "Tên miền có vẻ không đầy đủ", f"Tên máy chủ: {host}.", ["Kiểm tra xem có thiếu phần đuôi miền như .com hoặc .vn hay không."])

    flags = []
    serious = False
    if parts.scheme.lower() == "http":
        flags.append("Liên kết dùng HTTP, không mã hóa kết nối như HTTPS.")
    if "xn--" in host:
        flags.append("Tên miền chứa dạng punycode; cần kiểm tra kỹ ký tự có thể giả dạng tên miền quen thuộc.")
    if ip_literal:
        flags.append("Website dùng địa chỉ IP trực tiếp thay vì tên miền thông thường.")
    if host in SHORTENERS:
        flags.append("Đây là dịch vụ rút gọn link nên đích đến thật bị che khuất.")
    for brand, allowed in BRANDS.items():
        if brand in host and not any(host == d or host.endswith("." + d) for d in allowed):
            flags.append(f"Tên miền có chữ giống thương hiệu {brand} nhưng không nằm trên tên miền chính thức đã biết.")
            break
    labels = host.split(".")
    if len(labels) >= 6:
        flags.append("Tên miền có nhiều tầng tên miền phụ bất thường; kiểm tra kỹ tên miền chính.")
    path_tokens = set(re.findall(r"[a-z]+", (parts.path + " " + parts.query).lower()))
    matched_words = sorted(path_tokens & URL_WORDS)
    if len(matched_words) >= 3:
        flags.append("Đường dẫn chứa nhiều từ thường gặp trong lời mời đăng nhập/xác minh: " + ", ".join(matched_words) + ".")
    # Reputation checks are sent only to DNS/Safe Browsing APIs; the app does not open or crawl the submitted URL.
    if ip_literal:
        dns_ok = True
    else:
        dns_ok = dns_exists(host)
        if dns_ok is False:
            return result("warn", "Không tìm thấy bản ghi DNS cho tên miền", f"Tên miền được kiểm tra: {host}.", ["Tên miền có thể bị viết sai, chưa hoạt động hoặc mới được tạo.", "Điều này chưa đủ để kết luận là lừa đảo; hãy kiểm tra lại chính tả."] + flags)
        if dns_ok is None:
            flags.append("Không lấy được kết quả DNS trong lần kiểm tra này; trạng thái tên miền chưa xác minh.")

    threat, threat_note = google_safe_browsing(candidate)
    if threat is True:
        return result("danger", "Có cảnh báo nguy hiểm cho liên kết", f"Địa chỉ đã chuẩn hóa: {candidate}", [threat_note, *flags, "Không nhập mật khẩu, mã OTP, thông tin thanh toán hoặc tải tệp từ trang này."])
    if threat is None and os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip():
        # An explicitly configured reputation check that fails is itself an uncertainty.
        flags.append(threat_note)
    reputation_note = threat_note
    if flags:
        return result("warn", "Liên kết có điểm cần thận trọng", f"Địa chỉ đã chuẩn hóa: {candidate}", [*flags, reputation_note, "Không bấm tiếp nếu bạn không tin nguồn gửi link; HTTPS chỉ mã hóa kết nối và không chứng minh website đáng tin."])
    return result("safe", "Chưa phát hiện dấu hiệu rủi ro rõ ràng", f"Địa chỉ đã chuẩn hóa: {candidate}", ["Tên miền có phản hồi DNS.", reputation_note, "Đây không phải chứng nhận an toàn tuyệt đối; website mới hoặc chưa bị báo cáo vẫn có thể gây hại."])


@app.get("/")
def home():
    return render_template_string(PAGE)


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/check")
def api_check():
    data = request.get_json(silent=True) or {}
    kind = str(data.get("type", ""))[:20]
    value = str(data.get("value", ""))
    if not value.strip():
        return jsonify({"error": "Vui lòng nhập thông tin cần kiểm tra."}), 400
    if len(value) > 2048:
        return jsonify({"error": "Dữ liệu quá dài (tối đa 2048 ký tự)."}), 400
    handlers = {"phone": check_phone, "gmail": check_gmail, "tiktok": check_tiktok, "url": check_url}
    handler = handlers.get(kind)
    if not handler:
        return jsonify({"error": "Loại kiểm tra không được hỗ trợ."}), 400
    try:
        return jsonify(handler(value))
    except Exception:
        app.logger.exception("Unexpected validation error")
        return jsonify(result("neutral", "Chưa thể kiểm tra", "Đã xảy ra lỗi khi xử lý dữ liệu.", ["Thử lại với dữ liệu khác hoặc kiểm tra nhật ký của dịch vụ trên Render."])), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
