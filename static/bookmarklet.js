(function () {
  if (document.getElementById('_gsc_importer')) return;

  var API = 'https://web-production-538a6.up.railway.app';

  /* ── 데이터 추출 ── */
  function num(s) { return (s || '').replace(/[^0-9.]/g, ''); }

  function findVal(keywords) {
    var cells = document.querySelectorAll('th, td, dt, .label, .tit, .info-tit, [class*="label"], [class*="title"]');
    for (var i = 0; i < cells.length; i++) {
      var t = cells[i].textContent.trim();
      for (var k = 0; k < keywords.length; k++) {
        if (t.indexOf(keywords[k]) !== -1) {
          var next = cells[i].nextElementSibling;
          if (!next) next = cells[i].parentElement && cells[i].parentElement.querySelector('td:last-child, dd, .value, .cont');
          if (next && next !== cells[i]) return next.textContent.trim();
        }
      }
    }
    return '';
  }

  var pageName = (
    (document.querySelector('.bld_nm, .building_name, .bldname, .bld-name, h2.title, h1') || {}).textContent ||
    document.title.split(/[|\-–]/)[0]
  ).trim();

  var ex = {
    name:     pageName,
    address:  findVal(['주소','소재지','위치','지번']),
    year:     num(findVal(['준공','사용승인','건축연도','건축년도'])).slice(0,4),
    floor:    findVal(['층','해당층','임대층','소재층']),
    ownPY:    num(findVal(['전용면적','전용'])),
    rentPY:   num(findVal(['임대면적','공급면적','계약면적'])),
    deposit:  num(findVal(['보증금'])),
    rent:     num(findVal(['임대료','월세','월 임대료'])),
    mgmt:     num(findVal(['관리비'])),
  };

  /* ── 스타일 ── */
  var style = document.createElement('style');
  style.textContent = '#_gsc_importer *{box-sizing:border-box;font-family:-apple-system,sans-serif;}'
    + '#_gsc_importer input,#_gsc_importer select{width:100%;border:1px solid #dde1ec;border-radius:6px;padding:7px 9px;font-size:13px;background:#f5f7fb;color:#1a1f36;margin-top:3px;outline:none;}'
    + '#_gsc_importer input:focus,#_gsc_importer select:focus{border-color:#3b6ef5;box-shadow:0 0 0 3px rgba(59,110,245,.12);}'
    + '#_gsc_importer label{font-size:11px;font-weight:700;color:#8c93b0;letter-spacing:.4px;}'
    + '#_gsc_importer .gi-row{display:grid;gap:8px;}'
    + '#_gsc_importer .gi-col2{grid-template-columns:1fr 1fr;}'
    + '#_gsc_importer .gi-col3{grid-template-columns:1fr 1fr 1fr;}'
    + '#_gsc_importer .gi-sep{border:none;border-top:1px solid #ebeef5;margin:6px 0;}'
    + '#_gsc_importer .gi-section{font-size:11px;font-weight:700;color:#4a5278;letter-spacing:.5px;margin-bottom:2px;}'
    + '#_gsc_btn_ok{background:#3b6ef5;color:#fff;border:none;border-radius:8px;padding:10px;cursor:pointer;font-size:14px;font-weight:600;flex:1;transition:background .15s;}'
    + '#_gsc_btn_ok:hover{background:#2d5cd4;}'
    + '#_gsc_btn_cancel{background:#f0f2f7;color:#4a5278;border:none;border-radius:8px;padding:10px 16px;cursor:pointer;font-size:13px;}';
  document.head.appendChild(style);

  /* ── 모달 HTML ── */
  var districts = ['강남','서초','송파','여의도','마포','중구','기타'];
  var distOpts  = districts.map(function(d){ return '<option>'+d+'</option>'; }).join('');

  var wrap = document.createElement('div');
  wrap.id = '_gsc_importer';
  wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:2147483647;display:flex;align-items:center;justify-content:center;';
  wrap.innerHTML = '<div style="background:#fff;border-radius:14px;width:480px;max-height:92vh;overflow-y:auto;box-shadow:0 24px 64px rgba(0,0,0,.25);">'
    + '<div style="padding:16px 20px;border-bottom:1px solid #ebeef5;display:flex;justify-content:space-between;align-items:center;">'
    +   '<span style="font-size:15px;font-weight:700;color:#1a1f36">🏢 매물 등록 — 공실클럽</span>'
    +   '<button onclick="document.getElementById(\'_gsc_importer\').remove()" style="border:none;background:none;cursor:pointer;font-size:22px;color:#aaa;line-height:1">×</button>'
    + '</div>'
    + '<div style="padding:16px 20px;display:grid;gap:10px;">'
    +   '<div><label>건물명 *</label><input id="_gi_name" value="'+esc(ex.name)+'"></div>'
    +   '<div class="gi-row gi-col2">'
    +     '<div><label>지역</label><select id="_gi_district">'+distOpts+'</select></div>'
    +     '<div><label>준공연도</label><input id="_gi_year" value="'+esc(ex.year)+'" placeholder="예: 2010"></div>'
    +   '</div>'
    +   '<div><label>주소</label><input id="_gi_address" value="'+esc(ex.address)+'"></div>'
    +   '<hr class="gi-sep">'
    +   '<div class="gi-section">층별 임대 정보</div>'
    +   '<div class="gi-row gi-col3">'
    +     '<div><label>층</label><input id="_gi_floor" value="'+esc(ex.floor)+'" placeholder="예: 5층 일부"></div>'
    +     '<div><label>전용(평)</label><input id="_gi_ownPY" value="'+esc(ex.ownPY)+'"></div>'
    +     '<div><label>임대(평)</label><input id="_gi_rentPY" value="'+esc(ex.rentPY)+'"></div>'
    +   '</div>'
    +   '<div class="gi-row gi-col3">'
    +     '<div><label>보증금(만원)</label><input id="_gi_deposit" value="'+esc(ex.deposit)+'" placeholder="0"></div>'
    +     '<div><label>임대료(만원)</label><input id="_gi_rent" value="'+esc(ex.rent)+'" placeholder="0"></div>'
    +     '<div><label>관리비(만원)</label><input id="_gi_mgmt" value="'+esc(ex.mgmt)+'" placeholder="0"></div>'
    +   '</div>'
    +   '<div class="gi-row gi-col2">'
    +     '<div><label>공실상태</label><select id="_gi_vacancy"><option value="공실">공실</option><option value="공실예정">공실예정</option><option value="공실아님">임대중</option></select></div>'
    +     '<div><label>인테리어</label><select id="_gi_interior"><option value="무">무</option><option value="유">유</option></select></div>'
    +   '</div>'
    +   '<div id="_gi_msg" style="font-size:12px;color:#e5484d;display:none;padding:6px 10px;background:#fff5f5;border-radius:6px;"></div>'
    +   '<div style="display:flex;gap:8px;margin-top:4px;">'
    +     '<button id="_gsc_btn_ok">등록하기</button>'
    +     '<button id="_gsc_btn_cancel">취소</button>'
    +   '</div>'
    + '</div></div>';

  document.body.appendChild(wrap);

  document.getElementById('_gsc_btn_cancel').onclick = function(){ wrap.remove(); };

  document.getElementById('_gsc_btn_ok').onclick = async function() {
    var btn = document.getElementById('_gsc_btn_ok');
    var msg = document.getElementById('_gi_msg');
    var name = document.getElementById('_gi_name').value.trim();
    if (!name) { showMsg('건물명을 입력하세요.'); return; }

    btn.disabled = true; btn.textContent = '등록 중...';
    msg.style.display = 'none';

    try {
      var bldRes = await fetch(API + '/api/buildings', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          name: name,
          address:  document.getElementById('_gi_address').value.trim(),
          district: document.getElementById('_gi_district').value,
          year:     parseInt(document.getElementById('_gi_year').value) || 0
        })
      });
      if (!bldRes.ok) throw new Error('건물 등록 실패 (' + bldRes.status + ')');
      var bld = await bldRes.json();

      var ownPY  = parseFloat(document.getElementById('_gi_ownPY').value)  || 0;
      var rentPY = parseFloat(document.getElementById('_gi_rentPY').value) || 0;
      var rent   = parseInt(document.getElementById('_gi_rent').value)    || 0;
      var mgmt   = parseInt(document.getElementById('_gi_mgmt').value)    || 0;

      var floorRes = await fetch(API + '/api/buildings/' + bld.id + '/floors', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          floor:      document.getElementById('_gi_floor').value.trim(),
          ownAreaPY:  ownPY,  ownAreaSQM:  ownPY  ? +(ownPY*3.30579).toFixed(0)  : 0,
          rentAreaPY: rentPY, rentAreaSQM: rentPY ? +(rentPY*3.30579).toFixed(0) : 0,
          deposit:    parseInt(document.getElementById('_gi_deposit').value) || 0,
          rent: rent, mgmt: mgmt,
          vacancy:  document.getElementById('_gi_vacancy').value,
          interior: document.getElementById('_gi_interior').value
        })
      });
      if (!floorRes.ok) throw new Error('층 정보 등록 실패 (' + floorRes.status + ')');

      btn.textContent = '✓ 등록 완료!';
      btn.style.background = '#16a96b';
      setTimeout(function(){ wrap.remove(); }, 1800);
    } catch(e) {
      showMsg(e.message);
      btn.disabled = false;
      btn.textContent = '등록하기';
    }
  };

  function showMsg(t){ var m=document.getElementById('_gi_msg'); m.textContent=t; m.style.display='block'; }
  function esc(s){ return (s||'').replace(/"/g,'&quot;').replace(/</g,'&lt;'); }
})();
