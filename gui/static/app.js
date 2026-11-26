/* founder-id-checker dashboard. Plain JavaScript, no libraries, no network beyond this page's own server. */
(function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";
  var embedded = document.getElementById("state");
  var EXPORTED = !!embedded;
  var state = null;
  var currentDoc = null;
  var docCache = {};

  // ------------------------------------------------------------ words, in English and Indonesian

  var STR = {
    en: {
      nav_verdict: "Verdict", nav_months: "Months", nav_money: "Where it goes", nav_fixes: "Fixes", nav_channels: "Channels",
      nav_customers: "Customers", nav_compliance: "Papers", nav_board: "Board", nav_documents: "Documents",
      brand_sub: "business check-up", title: "Business check-up", loading: "Loading", live: "Live", stopped: "Server stopped",
      unreachable: "Cannot reach the server", exported_copy: "Exported copy",
      theme: "Colour theme", theme_auto: "Auto", theme_light: "Light", theme_dark: "Dark", lang_label: "Language",
      v_Sehat: "Healthy. Keep the routine and grow from here.",
      v_Waspada: "Watch out. The business works, but something is slipping.",
      v_Kritis: "Critical. Fix these before spending on anything else.",
      v_Incomplete: "Not enough real numbers yet. Run /checker-intake.",
      verdict_title: "Verdict", checkup_says: "The check-up says",
      months_note: "{n} months of real numbers, {a} to {b}", month_note: "1 month of real numbers, {a}", includes_est: "; includes estimates",
      no_checks: "No checks yet: there are no real numbers in checker/actuals.json.",
      status_ok: "OK", status_warn: "Warning", status_bad: "Critical",
      c_margin: "Net margin", c_breakeven: "Break-even", c_trend: "Trend", c_direct_cost: "Direct cost", c_labour: "Labour",
      c_owner: "Owner's drawings", c_owner_pay: "Owner's pay", c_debt: "Debt", c_cash: "Cash", c_platforms: "Platforms",
      c_customers: "Customers", c_compliance: "Papers and tax",
      t_net_sales: "Net sales a month", t_net_sales_s: "after discounts and the apps' cut",
      t_profit: "Net profit a month", t_profit_s: "{p} of net sales",
      t_be: "Against break-even", t_be_above: "{p} above", t_be_below: "{p} below", t_be_never: "never",
      t_be_s: "break-even {v} a month", t_be_s_never: "prices are below cost",
      t_kept: "Kept after owner and debt", t_kept_up: "added to cash each month", t_kept_down: "cash shrinks each month",
      t_cash: "Cash on hand", t_cash_s: "{w} weeks of running costs",
      run: "Run", run_end: ".",
      months_title: "Month by month", no_months: "No months yet.",
      ch_sales: "Net sales", ch_sales_sub: "the line is break-even, from the last 3 months",
      ch_kept: "Kept by the business", ch_kept_sub: "after the owner's drawings and the debt",
      ch_costs: "Direct cost and labour, share of net sales", ch_costs_sub: "thin lines are the targets",
      show_table: "Show as a table", col_month: "Month", col_net_sales: "Net sales", col_gross: "Gross", col_commission: "Commission",
      col_profit: "Net profit", col_owner: "Owner", col_debt: "Debt", col_kept: "Kept",
      l_direct: "Direct cost", l_direct_short: "Direct", l_labour: "Labour", l_labour_short: "Labour", target: "target {p}",
      breakeven: "Break-even", breakeven_label: "break-even {v}", days_open: "Days open", owner_takes: "Owner takes", never: "never",
      no_numbers_for: "No numbers for {m}.",
      money_title: "Where every Rp100.000 goes", money_card: "Of every Rp100.000 of net sales", average_of: "average of {m}",
      p_direct: "Direct cost", p_wages: "Wages", p_rent: "Rent and bills", p_tax: "Tax", p_profit: "Profit",
      money_loss: "The costs add up to more than net sales: every Rp100.000 of sales loses {v}.",
      col_part: "Part", col_of100: "Of Rp100.000", col_month_amt: "A month", no_numbers: "No numbers yet.",
      fixes_title: "Fixes, biggest first", no_fixes: "No fixes: nothing the numbers can put a Rupiah figure on.",
      fix_upto: "Up to {v} a month.", next: "Next:", fixes_note: "Each is the most that fix is worth on its own. They overlap, so do not add them up.",
      channels_title: "Channels", no_channels: "No channels yet.",
      ch_kept100: "Kept from every Rp100.000 of gross sales", ch_kept100_sub: "after the platform's commission and fees",
      col_channel: "Channel", col_gross_month: "Gross a month", col_share: "Share", col_orders: "Orders", col_avg_order: "Average order",
      platform_tag: "app or marketplace", tip_kept100: "Kept from Rp100.000", tip_share: "Share of gross",
      customers_title: "What customers say", no_customers: "No reviews or survey yet.",
      ratings_title: "Ratings, as each page shows them", ratings_sub: "across {n} reviews, weighted by review count", reviews_n: "{n} reviews",
      complaints_title: "Complaints in the reviews read", complaints_sub: "{n} read, worst first", thin: "(thin)",
      tip_reviews: "Reviews", tip_avg_stars: "Average stars",
      lapsed_title: "Customers who stopped buying", lapsed_sub: "{n} asked", lapsed_back: "Would really come back: {p} (only a ya counts).",
      ans_ya: "Ya", ans_mungkin: "Mungkin (counted as no)", ans_tidak: "Tidak", why_stopped: "Why they stopped",
      no_listings: "No listing ratings yet: the health check has no rating to judge.",
      compliance_title: "Permits, certificates and tax", no_compliance: "Not checked yet.",
      g_blocks: "Needed to keep selling", g_penalty: "A fine or sanction if missing", g_advised: "Advised",
      s_ok: "Done", s_missing: "Missing", s_expired: "Expired", s_unknown: "Not checked",
      checked_on: "Checked {d}. Rules change: confirm on the official page before acting.",
      board_title: "The board", so_far: "The check-up so far", board_vote: "The board's vote", no_board: "The board has not met yet.",
      lens: "{l} lens", lens_money: "Money", lens_customer: "Customer", lens_position: "Position", "lens_local-market": "Local market",
      score: "score {s} of 10", no_score: "no score found", done: "done", not_done: "not done yet",
      step_intake: "intake", step_health: "health", step_channels: "channels", step_customers: "customers",
      step_competitors: "competitors", step_compliance: "compliance", step_board: "board", step_report: "report",
      vote_GROW: "GROW", vote_FIX: "FIX", vote_PIVOT: "PIVOT", vote_CLOSE: "CLOSE",
      docs_title: "Documents", no_docs: "No documents yet. Each skill writes one into checker/.",
      docs_lang: "Documents are shown in the language the skills wrote them in.",
      doc_gone: "This document is not there any more.", doc_failed: "Could not load the document.",
      d_report: "Report", d_summary: "Summary", "d_plan-90": "90-day plan", "d_one-pager": "One-pager", d_business: "The business",
      d_health: "Health check", d_channels: "Channels", d_customers: "Customers", "d_customers-data": "Customer data",
      d_competitors: "Competitors", d_compliance: "Compliance", d_board: "Board",
      no_folder: "There is no checker/ folder at {d} yet. Run /checker-intake in that project.",
      footer: "Every number is the owner's own record; estimates are marked. Reviews and answers are from real customers. Not financial, legal or tax advice.",
      footer_live: "Read-only: this page never changes the files.", footer_export: "Exported copy: it does not update.",
      aria_sales: "Net sales by month", aria_kept: "Kept by the business by month", aria_costs: "Direct cost and labour by month",
      aria_channels: "What each channel keeps from every Rp100.000", aria_complaints: "Complaint themes by number of reviews",
      aria_reasons: "Reasons customers stopped buying",
      months_short: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
      units: ["k", "M", "B"], decimal: "."
    },
    id: {
      nav_verdict: "Hasil", nav_months: "Per bulan", nav_money: "Ke mana uangnya", nav_fixes: "Perbaikan", nav_channels: "Kanal",
      nav_customers: "Pelanggan", nav_compliance: "Izin", nav_board: "Dewan", nav_documents: "Dokumen",
      brand_sub: "cek kesehatan usaha", title: "Cek kesehatan usaha", loading: "Memuat", live: "Langsung", stopped: "Server berhenti",
      unreachable: "Server tidak bisa dihubungi", exported_copy: "Salinan ekspor",
      theme: "Tema warna", theme_auto: "Otomatis", theme_light: "Terang", theme_dark: "Gelap", lang_label: "Bahasa",
      v_Sehat: "Pertahankan kebiasaannya dan tumbuh dari sini.",
      v_Waspada: "Usahanya jalan, tapi ada yang mulai bocor.",
      v_Kritis: "Perbaiki ini dulu sebelum mengeluarkan uang untuk hal lain.",
      v_Incomplete: "Belum cukup angka nyata. Jalankan /checker-intake.",
      verdict_title: "Hasil", checkup_says: "Hasil pemeriksaan",
      months_note: "{n} bulan angka nyata, {a} s.d. {b}", month_note: "1 bulan angka nyata, {a}", includes_est: "; ada angka perkiraan",
      no_checks: "Belum ada pemeriksaan: checker/actuals.json belum berisi angka nyata.",
      status_ok: "Aman", status_warn: "Peringatan", status_bad: "Kritis",
      c_margin: "Margin bersih", c_breakeven: "Titik impas", c_trend: "Tren", c_direct_cost: "Biaya bahan", c_labour: "Biaya karyawan",
      c_owner: "Prive pemilik", c_owner_pay: "Gaji pemilik", c_debt: "Utang", c_cash: "Kas", c_platforms: "Platform",
      c_customers: "Pelanggan", c_compliance: "Izin dan pajak",
      t_net_sales: "Penjualan bersih sebulan", t_net_sales_s: "setelah diskon dan potongan aplikasi",
      t_profit: "Laba bersih sebulan", t_profit_s: "{p} dari penjualan bersih",
      t_be: "Dibanding titik impas", t_be_above: "{p} di atas", t_be_below: "{p} di bawah", t_be_never: "tidak pernah",
      t_be_s: "titik impas {v} sebulan", t_be_s_never: "harga di bawah biaya",
      t_kept: "Sisa setelah prive dan utang", t_kept_up: "menambah kas tiap bulan", t_kept_down: "kas berkurang tiap bulan",
      t_cash: "Kas di tangan", t_cash_s: "cukup {w} minggu biaya operasional",
      run: "Jalankan", run_end: ".",
      months_title: "Per bulan", no_months: "Belum ada angka bulanan.",
      ch_sales: "Penjualan bersih", ch_sales_sub: "garisnya titik impas, dari 3 bulan terakhir",
      ch_kept: "Sisa untuk usaha", ch_kept_sub: "setelah prive pemilik dan cicilan utang",
      ch_costs: "Biaya bahan dan karyawan, porsi dari penjualan bersih", ch_costs_sub: "garis tipis adalah target",
      show_table: "Tampilkan sebagai tabel", col_month: "Bulan", col_net_sales: "Penjualan bersih", col_gross: "Kotor", col_commission: "Komisi",
      col_profit: "Laba bersih", col_owner: "Prive", col_debt: "Utang", col_kept: "Sisa",
      l_direct: "Biaya bahan", l_direct_short: "Bahan", l_labour: "Biaya karyawan", l_labour_short: "Karyawan", target: "target {p}",
      breakeven: "Titik impas", breakeven_label: "titik impas {v}", days_open: "Hari buka", owner_takes: "Diambil pemilik", never: "tidak pernah",
      no_numbers_for: "Tidak ada angka untuk {m}.",
      money_title: "Ke mana setiap Rp100.000", money_card: "Dari setiap Rp100.000 penjualan bersih", average_of: "rata-rata {m}",
      p_direct: "Biaya bahan", p_wages: "Gaji", p_rent: "Sewa dan tagihan", p_tax: "Pajak", p_profit: "Laba",
      money_loss: "Biayanya lebih besar dari penjualan bersih: setiap Rp100.000 penjualan rugi {v}.",
      col_part: "Bagian", col_of100: "Dari Rp100.000", col_month_amt: "Sebulan", no_numbers: "Belum ada angka.",
      fixes_title: "Perbaikan, dari yang terbesar", no_fixes: "Tidak ada perbaikan yang bisa dihitung dalam Rupiah.",
      fix_upto: "Hingga {v} sebulan.", next: "Berikutnya:", fixes_note: "Angka tiap perbaikan dihitung sendiri-sendiri. Saling tumpang tindih, jadi jangan dijumlahkan.",
      channels_title: "Kanal penjualan", no_channels: "Belum ada kanal.",
      ch_kept100: "Yang tersisa dari setiap Rp100.000 penjualan kotor", ch_kept100_sub: "setelah komisi dan biaya platform",
      col_channel: "Kanal", col_gross_month: "Kotor sebulan", col_share: "Porsi", col_orders: "Pesanan", col_avg_order: "Rata-rata pesanan",
      platform_tag: "aplikasi atau marketplace", tip_kept100: "Sisa dari Rp100.000", tip_share: "Porsi penjualan kotor",
      customers_title: "Kata pelanggan", no_customers: "Belum ada ulasan atau survei.",
      ratings_title: "Rating, seperti tampil di tiap halaman", ratings_sub: "dari {n} ulasan, ditimbang jumlah ulasan", reviews_n: "{n} ulasan",
      complaints_title: "Keluhan di ulasan yang dibaca", complaints_sub: "{n} dibaca, mulai dari yang terburuk", thin: "(sedikit)",
      tip_reviews: "Ulasan", tip_avg_stars: "Rata-rata bintang",
      lapsed_title: "Pelanggan yang berhenti membeli", lapsed_sub: "{n} ditanya", lapsed_back: "Yang benar-benar mau kembali: {p} (hanya \"ya\" yang dihitung).",
      ans_ya: "Ya", ans_mungkin: "Mungkin (dihitung tidak)", ans_tidak: "Tidak", why_stopped: "Kenapa berhenti",
      no_listings: "Belum ada rating halaman: pemeriksaan belum bisa menilai rating.",
      compliance_title: "Izin, sertifikat dan pajak", no_compliance: "Belum dicek.",
      g_blocks: "Wajib agar tetap bisa berjualan", g_penalty: "Bisa kena denda atau sanksi", g_advised: "Disarankan",
      s_ok: "Sudah", s_missing: "Belum ada", s_expired: "Kedaluwarsa", s_unknown: "Belum dicek",
      checked_on: "Dicek {d}. Aturan bisa berubah: pastikan di situs resmi sebelum bertindak.",
      board_title: "Dewan direksi", so_far: "Kemajuan pemeriksaan", board_vote: "Suara dewan", no_board: "Dewan belum rapat.",
      lens: "Lensa {l}", lens_money: "Keuangan", lens_customer: "Pelanggan", lens_position: "Posisi", "lens_local-market": "Pasar lokal",
      score: "skor {s} dari 10", no_score: "skor tidak ditemukan", done: "selesai", not_done: "belum",
      step_intake: "data awal", step_health: "kesehatan", step_channels: "kanal", step_customers: "pelanggan",
      step_competitors: "pesaing", step_compliance: "izin", step_board: "dewan", step_report: "laporan",
      vote_GROW: "TUMBUH", vote_FIX: "PERBAIKI", vote_PIVOT: "UBAH ARAH", vote_CLOSE: "TUTUP",
      docs_title: "Dokumen", no_docs: "Belum ada dokumen. Setiap skill menulis satu ke checker/.",
      docs_lang: "Dokumen ditampilkan dalam bahasa yang ditulis oleh skill.",
      doc_gone: "Dokumen ini sudah tidak ada.", doc_failed: "Dokumen tidak bisa dimuat.",
      d_report: "Laporan", d_summary: "Ringkasan", "d_plan-90": "Rencana 90 hari", "d_one-pager": "Ringkasan satu halaman", d_business: "Profil usaha",
      d_health: "Cek kesehatan", d_channels: "Kanal", d_customers: "Pelanggan", "d_customers-data": "Data pelanggan",
      d_competitors: "Pesaing", d_compliance: "Izin", d_board: "Dewan",
      no_folder: "Belum ada folder checker/ di {d}. Jalankan /checker-intake di proyek itu.",
      footer: "Semua angka dari catatan pemilik sendiri; angka perkiraan ditandai. Ulasan dan jawaban dari pelanggan nyata. Bukan nasihat keuangan, hukum atau pajak.",
      footer_live: "Hanya baca: halaman ini tidak pernah mengubah file.", footer_export: "Salinan ekspor: tidak diperbarui.",
      aria_sales: "Penjualan bersih per bulan", aria_kept: "Sisa untuk usaha per bulan", aria_costs: "Biaya bahan dan karyawan per bulan",
      aria_channels: "Yang tersisa dari setiap Rp100.000 per kanal", aria_complaints: "Tema keluhan menurut jumlah ulasan",
      aria_reasons: "Alasan pelanggan berhenti membeli",
      months_short: ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
      units: ["rb", "jt", "M"], decimal: ","
    }
  };

  var lang = "";
  try { lang = localStorage.getItem("checker-lang") || ""; } catch (e) { lang = ""; }
  if (!STR[lang]) lang = /^id\b/i.test(navigator.language || "") ? "id" : "en";

  function t(key, vars) {
    var s = STR[lang][key];
    if (s == null) s = STR.en[key];
    if (s == null) return key;
    if (vars) s = s.replace(/\{(\w+)\}/g, function (_, k) { return vars[k] != null ? vars[k] : ""; });
    return s;
  }
  function pick(obj, field) { return lang === "id" && obj[field + "_id"] ? obj[field + "_id"] : obj[field]; }

  var VERDICT_ICON = { Sehat: "✓", Waspada: "!", Kritis: "✗", Incomplete: "?" };
  var MARK = { ok: "✓", warn: "!", bad: "✗" };

  // ------------------------------------------------------------ helpers

  function el(tag, attrs) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (attrs[k] == null) continue;
      if (k === "text") n.textContent = attrs[k];
      else if (k === "cls") n.className = attrs[k];
      else if (k === "style") n.style.cssText = attrs[k];  // through the DOM, so the page's CSP allows it
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    }
    for (var i = 2; i < arguments.length; i++) add(n, arguments[i]);
    return n;
  }
  function add(n, c) {
    if (c == null || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { add(n, x); }); return; }
    n.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  }
  function svg(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) if (attrs[k] != null) {
      if (k === "text") n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]);
    }
    for (var i = 2; i < arguments.length; i++) if (arguments[i]) n.appendChild(arguments[i]);
    return n;
  }
  function dots(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
  function rp(v) { if (v == null || isNaN(v)) return "?"; var s = v < 0 ? "-" : ""; return s + "Rp" + dots(Math.round(Math.abs(v))); }
  function dec(x, d) { return x.toFixed(d).replace(".", t("decimal")); }
  function rpShort(v) {
    var a = Math.abs(v), s = v < 0 ? "-" : "", u = t("units");
    var r = function (x) { return (Math.round(x * 10) / 10).toString().replace(".", t("decimal")); };
    if (a >= 1e9) return s + "Rp" + r(a / 1e9) + " " + u[2];
    if (a >= 1e6) return s + "Rp" + r(a / 1e6) + " " + u[1];
    if (a >= 1e3) return s + "Rp" + r(a / 1e3) + " " + u[0];
    return s + "Rp" + Math.round(a);
  }
  function pct(v, d) { if (v == null || isNaN(v)) return "?"; return dec(v * 100, d == null ? 1 : d) + "%"; }
  function monthName(m) { var p = String(m).split("-"); return t("months_short")[(+p[1] || 1) - 1] + " " + p[0]; }
  function niceMax(v) {
    if (v <= 0) return 1;
    var e = Math.pow(10, Math.floor(Math.log10(v))), f = v / e;
    var n = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
    return n * e;
  }
  function section(id, title) { var s = el("section", { id: id }); s.appendChild(el("h2", { text: title })); return s; }
  function empty(text, skill) {
    return el("p", { cls: "empty" }, text, skill ? [" " + t("run") + " ", el("code", { text: "/" + skill }), t("run_end")] : null);
  }
  function mark(status) { return el("span", { cls: "mark " + status, "aria-hidden": "true", text: MARK[status] || "" }); }
  function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

  // ------------------------------------------------------------ tooltip

  var tip = document.getElementById("tip");
  function showTip(evt, rows) {
    tip.textContent = "";
    rows.forEach(function (r, i) {
      if (typeof r === "string") { tip.appendChild(el(i === 0 ? "b" : "div", { text: r })); if (i === 0) tip.appendChild(el("br")); return; }
      var key = el("span", null, r.color ? el("i", { style: "background:" + r.color }) : null, r.label);
      tip.appendChild(el("div", { cls: "row" }, key, el("span", { text: r.value })));
    });
    tip.style.display = "block";
    moveTip(evt);
  }
  function moveTip(evt) {
    var x = evt.clientX + 14, y = evt.clientY + 14, w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > window.innerWidth - 8) x = evt.clientX - w - 14;
    if (y + h > window.innerHeight - 8) y = evt.clientY - h - 14;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  function hideTip() { tip.style.display = "none"; }
  function hover(node, rows) {
    node.addEventListener("mouseenter", function (e) { node.classList.add("on"); showTip(e, rows()); });
    node.addEventListener("mousemove", moveTip);
    node.addEventListener("mouseleave", function () { node.classList.remove("on"); hideTip(); });
  }

  // ------------------------------------------------------------ chart pieces

  function frame(container, height) {
    var W = Math.max(240, Math.round(container.clientWidth || 640));
    var s = svg("svg", { viewBox: "0 0 " + W + " " + height, role: "img" });
    return { svg: s, W: W, H: height };
  }
  function isNice(step) { var e = Math.pow(10, Math.floor(Math.log10(step))), r = Math.round(step / e * 100) / 100; return [1, 2, 2.5, 5].indexOf(r) >= 0; }
  function yAxis(g, f, max, min, fmt) {
    var steps = [4, 5, 2, 3].filter(function (n) { return isNice((max - min) / n); })[0] || 4;
    for (var i = 0; i <= steps; i++) {
      var v = min + (max - min) * i / steps, y = f.y(v);
      g.appendChild(svg("line", { x1: f.left, x2: f.W - f.right, y1: y, y2: y, "class": v === 0 ? "baseline" : "gridline" }));
      g.appendChild(svg("text", { x: f.left - 8, y: y + 4, "text-anchor": "end", text: fmt(v) }));
    }
  }
  function xLabels(g, f, months) {
    var every = Math.ceil(months.length / Math.max(1, Math.floor((f.W - f.left - f.right) / 44)));
    months.forEach(function (m, i) {
      if (i % every && i !== months.length - 1) return;
      var p = String(m).split("-"), yearToo = i === 0 || p[1] === "01";  // the year only where it changes
      g.appendChild(svg("text", { x: f.x(i) + f.band / 2, y: f.H - 6, "text-anchor": "middle",
        text: yearToo ? monthName(m) : t("months_short")[(+p[1] || 1) - 1] }));
    });
  }
  // a column with a 4px rounded data end, square at the baseline
  function column(x, y0, y1, w, color) {
    var top = Math.min(y0, y1), h = Math.abs(y1 - y0), r = Math.min(4, h, w / 2), up = y1 <= y0;
    if (h < 0.5) return svg("rect", { x: x, y: y0 - 0.5, width: w, height: 1, fill: color });
    var d = up
      ? "M" + x + "," + (top + h) + "V" + (top + r) + "Q" + x + "," + top + " " + (x + r) + "," + top + "H" + (x + w - r) +
        "Q" + (x + w) + "," + top + " " + (x + w) + "," + (top + r) + "V" + (top + h) + "Z"
      : "M" + x + "," + top + "V" + (top + h - r) + "Q" + x + "," + (top + h) + " " + (x + r) + "," + (top + h) + "H" + (x + w - r) +
        "Q" + (x + w) + "," + (top + h) + " " + (x + w) + "," + (top + h - r) + "V" + top + "Z";
    return svg("path", { d: d, fill: color });
  }
  function bar(x0, x1, y, h, color) { // horizontal, rounded at the data end
    var w = Math.max(1, x1 - x0), r = Math.min(4, w, h / 2);
    return svg("path", { d: "M" + x0 + "," + y + "H" + (x0 + w - r) + "Q" + (x0 + w) + "," + y + " " + (x0 + w) + "," + (y + r) +
      "V" + (y + h - r) + "Q" + (x0 + w) + "," + (y + h) + " " + (x0 + w - r) + "," + (y + h) + "H" + x0 + "Z", fill: color });
  }
  function tableView(head, rows) {
    return el("details", { cls: "table" }, el("summary", { text: t("show_table") }),
      el("div", { cls: "scroll" }, el("table", null,
        el("thead", null, el("tr", null, head.map(function (h, i) { return el("th", { cls: i ? "num" : null, text: h }); }))),
        el("tbody", null, rows.map(function (r) {
          return el("tr", null, r.map(function (c, i) { return el("td", { cls: i ? "num" : null, text: c }); }));
        })))));
  }
  function legend(items) {
    return el("div", { cls: "legend" }, items.map(function (it) {
      return el("span", null, el("i", { cls: it.line ? "line" : null, style: "background:" + it.color }), it.label);
    }));
  }
  function chartCard(title, sub, body) {
    return el("div", { cls: "card" }, el("div", { cls: "chart-head" }, el("h3", { text: title }), sub ? el("span", { cls: "sub", text: sub }) : null), body);
  }

  // Monthly columns, one series, optional horizontal reference line. Negative values hang below zero.
  function monthColumns(host, months, values, opt) {
    var f = frame(host, 240);
    f.left = 64; f.right = 16; f.top = 16; f.bottom = 28;
    var hi = Math.max.apply(null, values.concat([opt.ref || 0, 0])), lo = Math.min.apply(null, values.concat([0]));
    var max = niceMax(hi * 1.08), min = lo < 0 ? -niceMax(-lo * 1.08) : 0;
    var plotH = f.H - f.top - f.bottom, plotW = f.W - f.left - f.right;
    f.band = plotW / months.length;
    f.x = function (i) { return f.left + i * f.band; };
    f.y = function (v) { return f.top + (max - v) / (max - min) * plotH; };
    var g = svg("g");
    yAxis(g, f, max, min, rpShort);
    if (min < 0) g.appendChild(svg("line", { x1: f.left, x2: f.W - f.right, y1: f.y(0), y2: f.y(0), "class": "baseline" }));
    var w = Math.min(24, f.band * 0.6);
    months.forEach(function (m, i) {
      var v = values[i];
      var hit = svg("rect", { x: f.x(i), y: f.top, width: f.band, height: plotH, "class": "hit" });
      g.appendChild(hit);
      g.appendChild(column(f.x(i) + (f.band - w) / 2, f.y(0), f.y(v), w, v < 0 ? opt.negColor : opt.color));
      hover(hit, function () { return opt.tip(i); });
    });
    if (opt.ref) {
      var ry = f.y(opt.ref);
      g.appendChild(svg("line", { x1: f.left, x2: f.W - f.right, y1: ry, y2: ry, "class": "refline" }));
      g.appendChild(svg("text", { x: f.W - f.right, y: ry - 6, "text-anchor": "end", "class": "ink halo", text: opt.refLabel }));
    }
    // label only the latest month
    var last = values.length - 1;
    g.appendChild(svg("text", { x: f.x(last) + f.band / 2, y: values[last] < 0 ? f.y(values[last]) + 16 : f.y(values[last]) - 6,
      "text-anchor": "middle", "class": "ink halo", text: rpShort(values[last]) }));
    xLabels(g, f, months);
    f.svg.appendChild(g);
    f.svg.setAttribute("aria-label", opt.aria);
    host.appendChild(f.svg);
  }

  // Monthly lines (shares), one axis in percent, each with its own target line.
  function monthLines(host, months, series) {
    var f = frame(host, 240);
    f.left = 48; f.right = 110; f.top = 16; f.bottom = 28;
    var all = [];
    series.forEach(function (s) { all = all.concat(s.values, s.target != null ? [s.target] : []); });
    var max = Math.min(1, niceMax(Math.max.apply(null, all) * 1.15)), min = 0;
    var plotH = f.H - f.top - f.bottom, plotW = f.W - f.left - f.right;
    f.band = plotW / months.length;
    f.x = function (i) { return f.left + i * f.band; };
    f.y = function (v) { return f.top + (max - v) / (max - min) * plotH; };
    var g = svg("g");
    yAxis(g, f, max, min, function (v) { return Math.round(v * 100) + "%"; });
    var cx = function (i) { return f.x(i) + f.band / 2; };
    series.forEach(function (s) {
      if (s.target != null) {
        var ty = f.y(s.target);
        g.appendChild(svg("line", { x1: f.left, x2: f.W - f.right, y1: ty, y2: ty, stroke: s.color, "stroke-width": 1, "stroke-opacity": 0.55 }));
      }
    });
    series.forEach(function (s) {
      var d = s.values.map(function (v, i) { return (i ? "L" : "M") + cx(i) + "," + f.y(v); }).join("");
      g.appendChild(svg("path", { d: d, fill: "none", stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));
      var li = s.values.length - 1;
      g.appendChild(svg("circle", { cx: cx(li), cy: f.y(s.values[li]), r: 4, fill: s.color, stroke: cssVar("--surface"), "stroke-width": 2 }));
      g.appendChild(svg("text", { x: cx(li) + 10, y: f.y(s.values[li]) + 4, "class": "ink halo", text: s.short + " " + pct(s.values[li], 0) }));
    });
    var cross = svg("line", { y1: f.top, y2: f.top + plotH, stroke: cssVar("--axis"), "stroke-width": 1, visibility: "hidden" });
    g.appendChild(cross);
    months.forEach(function (m, i) {
      var hit = svg("rect", { x: f.x(i), y: f.top, width: f.band, height: plotH, "class": "hit" });
      hit.addEventListener("mouseenter", function (e) {
        cross.setAttribute("x1", cx(i)); cross.setAttribute("x2", cx(i)); cross.setAttribute("visibility", "visible");
        showTip(e, [monthName(m)].concat(series.map(function (s) {
          return { color: s.color, label: s.label, value: pct(s.values[i]) + (s.target != null ? " (" + t("target", { p: pct(s.target, 0) }) + ")" : "") };
        })));
      });
      hit.addEventListener("mousemove", moveTip);
      hit.addEventListener("mouseleave", function () { cross.setAttribute("visibility", "hidden"); hideTip(); });
      g.appendChild(hit);
    });
    xLabels(g, f, months);
    f.svg.appendChild(g);
    f.svg.setAttribute("aria-label", t("aria_costs"));
    host.appendChild(f.svg);
  }

  // One horizontal stacked bar (parts of a whole), 2px surface gap between segments.
  function stackBar(host, parts, total, fmt) {
    var f = frame(host, 40), x = 0, gap = 2, w = f.W;
    var g = svg("g");
    var shown = parts.filter(function (p) { return p.value > 0; });
    shown.forEach(function (p) {
      var pw = p.value / total * (w - gap * (shown.length - 1));
      var r = svg("rect", { x: x, y: 8, width: Math.max(1, pw), height: 24, fill: p.color });
      r.style.pointerEvents = "all";
      g.appendChild(r);
      if (pw > 64) {
        var label = svg("text", { x: x + 8, y: 24, text: fmt(p.value) });
        label.style.fill = p.darkText ? "#0b0b0b" : "#ffffff";
        g.appendChild(label);
      }
      hover(r, function () { return [p.label, { color: p.color, label: "", value: fmt(p.value) }]; });
      x += pw + gap;
    });
    f.svg.appendChild(g);
    f.svg.setAttribute("aria-label", parts.map(function (p) { return p.label + " " + fmt(p.value); }).join(", "));
    host.appendChild(f.svg);
  }

  // Horizontal bars with the label on the left and the value at the tip.
  function hBars(host, rows, opt) {
    var rowH = 30, f = frame(host, rows.length * rowH + 8);
    var labelW = Math.min(180, f.W * 0.35), valueW = 120, plotW = f.W - labelW - valueW;
    var max = opt.max || Math.max.apply(null, rows.map(function (r) { return r.value; }).concat([1]));
    var g = svg("g");
    rows.forEach(function (r, i) {
      var y = i * rowH + 4;
      g.appendChild(svg("text", { x: 0, y: y + 15, "class": "ink", text: r.label.length > 26 ? r.label.slice(0, 25) + "…" : r.label }));
      var x1 = labelW + Math.max(0, r.value) / max * plotW;
      g.appendChild(bar(labelW, x1, y + 4, 14, r.color || opt.color));
      g.appendChild(svg("text", { x: x1 + 8, y: y + 15, text: opt.fmt(r.value) + (r.extra ? "  " + r.extra : "") }));
      var hit = svg("rect", { x: 0, y: y, width: f.W, height: rowH - 2, "class": "hit" });
      g.insertBefore(hit, g.firstChild);
      hover(hit, function () { return r.tip || [r.label, { label: "", value: opt.fmt(r.value) }]; });
    });
    f.svg.appendChild(g);
    f.svg.setAttribute("aria-label", opt.aria);
    host.appendChild(f.svg);
  }

  // ------------------------------------------------------------ sections

  function renderVerdict(st) {
    var h = st.health, v = st.verdict, icon = VERDICT_ICON[v] || "?";
    var s = section("verdict", t("verdict_title"));
    var note = null;
    if (h && h.months.length) {
      var ms = h.months;
      note = (ms.length > 1 ? t("months_note", { n: ms.length, a: monthName(ms[0].month), b: monthName(ms[ms.length - 1].month) })
        : t("month_note", { a: monthName(ms[0].month) })) + (h.estimates && h.estimates.length ? t("includes_est") : "");
    }
    var left = el("div", { cls: "card verdict " + v },
      el("div", { cls: "label", text: t("checkup_says") }),
      el("div", { cls: "word" }, el("span", { cls: "badge", "aria-hidden": "true", text: icon }), v),
      el("div", { cls: "means", text: t("v_" + v) }),
      note ? el("div", { cls: "note", text: note }) : null);
    var right = el("div", { cls: "card" });
    if (h && h.checks.length) {
      var rank = { bad: 0, warn: 1, ok: 2 };
      var ordered = h.checks.slice().sort(function (a, b) { return rank[a.status] - rank[b.status]; });  // problems first
      right.appendChild(el("ul", { cls: "checks" }, ordered.map(function (c) {
        return el("li", null, mark(c.status), el("div", null,
          el("span", { cls: "sr-only", text: t("status_" + c.status) + ": " }), pick(c, "text"),
          el("span", { cls: "tag", text: t("c_" + c.id) })));
      })));
    } else right.appendChild(empty(t("no_checks"), "checker-intake"));
    s.appendChild(el("div", { cls: "hero" }, left, right));
    if (h && h.recent) {
      var R = h.recent, cov = h.breakeven_month ? R.net_sales / h.breakeven_month : null;
      var tiles = [
        { k: t("t_net_sales"), v: rp(R.net_sales), s: t("t_net_sales_s") },
        { k: t("t_profit"), v: rp(R.net_profit), s: t("t_profit_s", { p: pct(R.net_profit / R.net_sales) }) },
        { k: t("t_be"), v: cov == null ? t("t_be_never") : t(cov >= 1 ? "t_be_above" : "t_be_below", { p: pct(Math.abs(cov - 1), 0) }),
          s: h.breakeven_month ? t("t_be_s", { v: rp(h.breakeven_month) }) : t("t_be_s_never") },
        { k: t("t_kept"), v: rp(R.kept), s: t(R.kept < 0 ? "t_kept_down" : "t_kept_up") }
      ];
      if (h.cash) tiles.push({ k: t("t_cash"), v: rp(h.cash.balance), s: t("t_cash_s", { w: dec(h.cash.weeks_covered || 0, 1) }) });
      s.appendChild(el("div", { cls: "tiles" }, tiles.map(function (x) {
        return el("div", { cls: "card tile" }, el("div", { cls: "k", text: x.k }), el("div", { cls: "v", text: x.v }), el("div", { cls: "s", text: x.s }));
      })));
    }
    return s;
  }

  function renderMonths(st) {
    var s = section("months", t("months_title")), h = st.health;
    if (!h || !h.months.length) { s.appendChild(el("div", { cls: "card" }, empty(t("no_months"), "checker-intake"))); return s; }
    var ms = h.months.map(function (m) { return m.month; });
    var grid = el("div", { cls: "grid two" });
    var c1 = el("div", { cls: "chart" });
    var be = h.breakeven_month;
    grid.appendChild(chartCard(t("ch_sales"), t("ch_sales_sub"), el("div", null, c1,
      tableView([t("col_month"), t("col_net_sales"), t("col_gross"), t("col_commission")], h.months.map(function (m) {
        return [monthName(m.month), rp(m.net_sales), rp(m.gross), rp(m.commission)];
      })))));
    var c2 = el("div", { cls: "chart" });
    grid.appendChild(chartCard(t("ch_kept"), t("ch_kept_sub"), el("div", null, c2,
      tableView([t("col_month"), t("col_profit"), t("col_owner"), t("col_debt"), t("col_kept")], h.months.map(function (m) {
        return [monthName(m.month), rp(m.net_profit), rp(m.owner_drawings), rp(m.debt_payment), rp(m.kept)];
      })))));
    s.appendChild(grid);
    var tg = h.targets || {}, series = [
      { label: t("l_direct"), short: t("l_direct_short"), color: cssVar("--s1"), target: tg.direct_cost_pct,
        values: h.months.map(function (m) { return m.direct_cost / m.net_sales; }) },
      { label: t("l_labour"), short: t("l_labour_short"), color: cssVar("--s2"), target: tg.labour_pct,
        values: h.months.map(function (m) { return m.labour / m.net_sales; }) }
    ];
    var c3 = el("div", { cls: "chart" });
    s.appendChild(el("div", { style: "margin-top:16px" }, chartCard(t("ch_costs"), t("ch_costs_sub"),
      el("div", null, legend(series.map(function (x) {
        return { label: x.label + (x.target != null ? " (" + t("target", { p: pct(x.target, 0) }) + ")" : ""), color: x.color, line: true };
      })), c3, tableView([t("col_month"), t("l_direct"), t("l_labour")], h.months.map(function (m, i) {
        return [monthName(m.month), pct(series[0].values[i]), pct(series[1].values[i])];
      }))))));
    if (h.missing_months && h.missing_months.length) {
      s.appendChild(el("p", { cls: "small muted", text: t("no_numbers_for", { m: h.missing_months.map(monthName).join(", ") }) }));
    }
    later(function () {
      monthColumns(c1, ms, h.months.map(function (m) { return m.net_sales; }), {
        color: cssVar("--s1"), negColor: cssVar("--critical"), ref: be, refLabel: be ? t("breakeven_label", { v: rpShort(be) }) : "",
        aria: t("aria_sales"), tip: function (i) {
          var m = h.months[i];
          return [monthName(m.month), { color: cssVar("--s1"), label: t("col_net_sales"), value: rp(m.net_sales) },
            { label: t("breakeven"), value: be ? rp(be) : t("never") }, { label: t("days_open"), value: String(m.days_open) }];
        }
      });
      monthColumns(c2, ms, h.months.map(function (m) { return m.kept; }), {
        color: cssVar("--s1"), negColor: cssVar("--critical"), aria: t("aria_kept"), tip: function (i) {
          var m = h.months[i];
          return [monthName(m.month), { label: t("col_profit"), value: rp(m.net_profit) }, { label: t("owner_takes"), value: rp(m.owner_drawings) },
            { label: t("col_debt"), value: rp(m.debt_payment) },
            { color: m.kept < 0 ? cssVar("--critical") : cssVar("--s1"), label: t("col_kept"), value: rp(m.kept) }];
        }
      });
      monthLines(c3, ms, series);
    });
    return s;
  }

  function renderMoney(st) {
    var s = section("money", t("money_title")), h = st.health;
    if (!h || !h.recent) { s.appendChild(el("div", { cls: "card" }, empty(t("no_numbers"), "checker-intake"))); return s; }
    var R = h.recent, per = 100000 / R.net_sales;
    var parts = [
      { label: t("p_direct"), value: R.direct_cost * per, color: cssVar("--s1") },
      { label: t("p_wages"), value: R.labour * per, color: cssVar("--s2") },
      { label: t("p_rent"), value: (R.fixed_costs + R.other_costs) * per, color: cssVar("--s3") },
      { label: t("p_tax"), value: R.pph_final * per, color: cssVar("--s4"), darkText: true },
      { label: t("p_profit"), value: Math.max(0, R.net_profit) * per, color: cssVar("--s5") }
    ];
    var c = el("div", { cls: "chart" });
    var total = parts.reduce(function (a, p) { return a + p.value; }, 0);
    var loss = R.net_profit < 0 ? el("p", { cls: "small", text: t("money_loss", { v: rp(-R.net_profit * per) }) }) : null;
    s.appendChild(chartCard(t("money_card"), t("average_of", { m: h.recent_months.map(monthName).join(", ") }),
      el("div", null, legend(parts.map(function (p) { return { label: p.label + " " + rp(p.value), color: p.color }; })), c, loss,
        tableView([t("col_part"), t("col_of100"), t("col_month_amt")], parts.map(function (p) { return [p.label, rp(p.value), rp(p.value / per)]; })))));
    later(function () { stackBar(c, parts, total, rp); });
    return s;
  }

  function renderFixes(st) {
    var s = section("fixes", t("fixes_title")), h = st.health, card = el("div", { cls: "card" });
    s.appendChild(card);
    if (!h || !h.fixes || !h.fixes.length) { card.appendChild(empty(h ? t("no_fixes") : t("no_numbers"), h ? null : "checker-intake")); return s; }
    var max = h.fixes[0].rupiah_per_month;
    h.fixes.forEach(function (f, i) {
      card.appendChild(el("div", { cls: "fix" }, el("div", { cls: "n", text: String(i + 1) }), el("div", null,
        el("div", null, el("span", { cls: "amt", text: t("fix_upto", { v: rp(f.rupiah_per_month) }) + " " }), pick(f, "text")),
        el("div", { cls: "bar", style: "width:" + Math.max(2, f.rupiah_per_month / max * 100) + "%" }),
        el("div", { cls: "next" }, t("next") + " ", el("code", { text: "/" + f.skill })))));
    });
    card.appendChild(el("p", { cls: "small muted", text: t("fixes_note") }));
    return s;
  }

  function renderChannels(st) {
    var s = section("channels", t("channels_title")), h = st.health;
    if (!h || !h.channels || !h.channels.length) { s.appendChild(el("div", { cls: "card" }, empty(t("no_channels"), "checker-intake"))); return s; }
    var c = el("div", { cls: "chart" });
    var head = [t("col_channel"), t("col_gross_month"), t("col_share"), t("col_commission"), t("col_orders"), t("col_avg_order")];
    s.appendChild(chartCard(t("ch_kept100"), t("ch_kept100_sub"), el("div", null, c,
      el("div", { cls: "scroll", style: "margin-top:12px" }, el("table", null,
        el("thead", null, el("tr", null, head.map(function (x, i) { return el("th", { cls: i ? "num" : null, text: x }); }))),
        el("tbody", null, h.channels.map(function (r) {
          return el("tr", null, el("td", null, r.channel, r.platform ? el("span", { cls: "tag muted small", text: "  " + t("platform_tag") }) : null),
            el("td", { cls: "num", text: rp(r.gross) }), el("td", { cls: "num", text: pct(r.share, 0) }),
            el("td", { cls: "num", text: rp(r.commission) + " (" + pct(r.commission_rate) + ")" }),
            el("td", { cls: "num", text: r.orders ? dots(Math.round(r.orders)) : "?" }), el("td", { cls: "num", text: r.avg_order ? rp(r.avg_order) : "?" }));
        })))))));
    later(function () {
      hBars(c, h.channels.map(function (r) {
        return { label: r.channel, value: r.kept_per_100k, tip: [r.channel, { label: t("tip_kept100"), value: rp(r.kept_per_100k) },
          { label: t("col_commission"), value: pct(r.commission_rate) }, { label: t("tip_share"), value: pct(r.share, 0) }] };
      }), { color: cssVar("--s1"), fmt: rp, max: 100000, aria: t("aria_channels") });
    });
    return s;
  }

  function renderCustomers(st) {
    var s = section("customers", t("customers_title")), cu = st.customers;
    if (!cu) { s.appendChild(el("div", { cls: "card" }, empty(t("no_customers"), "checker-customers"))); return s; }
    var grid = el("div", { cls: "grid two" });
    if (cu.listings && cu.listings.length) {
      grid.appendChild(el("div", { cls: "card" }, el("div", { cls: "chart-head" }, el("h3", { text: t("ratings_title") })),
        el("div", { cls: "tile" }, el("div", { cls: "v", text: dec(Number(cu.rating_avg), 1) + " ★" }),
          el("div", { cls: "s", text: t("ratings_sub", { n: dots(cu.reviews) }) })),
        el("table", { style: "margin-top:10px" }, el("tbody", null, cu.listings.map(function (l) {
          return el("tr", null, el("td", { text: l.source }), el("td", { cls: "num", text: dec(Number(l.rating), 1) + " ★" }),
            el("td", { cls: "num", text: t("reviews_n", { n: dots(l.reviews) }) }));
        })))));
    }
    var rt = cu.review_tally;
    if (rt && rt.complaints && rt.complaints.length) {
      var c = el("div", { cls: "chart" });
      grid.appendChild(chartCard(t("complaints_title"), t("complaints_sub", { n: rt.reviews }), el("div", null, c)));
      later(function () {
        hBars(c, rt.complaints.slice(0, 8).map(function (x) {
          var q = x.quotes && x.quotes[0];
          return { label: x.theme, value: x.count, extra: x.thin ? t("thin") : "",
            tip: [x.theme, { label: t("tip_reviews"), value: String(x.count) }, { label: t("tip_avg_stars"), value: dec(x.avg_stars, 1) }]
              .concat(q ? ["“" + q.quote + "”"] : []) };
        }), { color: cssVar("--s1"), fmt: function (v) { return String(v); }, aria: t("aria_complaints") });
      });
    }
    var sv = cu.survey;
    if (sv) {
      var c2 = el("div", { cls: "chart" }), c3 = el("div", { cls: "chart" }), w = sv.would_return;
      var parts = [{ label: t("ans_ya"), value: w.ya, color: cssVar("--s1") },
        { label: t("ans_mungkin"), value: w.mungkin, color: cssVar("--s4"), darkText: true },
        { label: t("ans_tidak"), value: w.tidak, color: cssVar("--s2") }];
      grid.appendChild(chartCard(t("lapsed_title"), t("lapsed_sub", { n: sv.answers }), el("div", null,
        el("p", { cls: "small", text: t("lapsed_back", { p: pct(sv.return_rate, 0) }) }),
        legend(parts.map(function (p) { return { label: p.label + " " + p.value, color: p.color }; })), c2,
        el("h3", { style: "font-size:14px;margin:14px 0 0", text: t("why_stopped") }), c3)));
      later(function () {
        stackBar(c2, parts, sv.answers, function (v) { return String(v); });
        hBars(c3, sv.reasons.map(function (r) { return { label: r.reason, value: r.count, extra: r.thin ? t("thin") : "" }; }),
          { color: cssVar("--s1"), fmt: function (v) { return String(v); }, aria: t("aria_reasons") });
      });
    }
    s.appendChild(grid);
    if (!cu.listings) s.appendChild(el("p", { cls: "small muted", text: t("no_listings") }));
    return s;
  }

  function renderCompliance(st) {
    var s = section("compliance", t("compliance_title")), co = st.compliance, card = el("div", { cls: "card" });
    s.appendChild(card);
    if (!co || !co.items || !co.items.length) { card.appendChild(empty(t("no_compliance"), "checker-compliance")); return s; }
    var groups = [["blocks_sales", t("g_blocks")], ["penalty", t("g_penalty")], ["advised", t("g_advised")]];
    var look = { ok: "ok", missing: "bad", expired: "bad", unknown: "todo" };
    groups.forEach(function (g) {
      var items = co.items.filter(function (i) { return i.severity === g[0]; });
      if (!items.length) return;
      card.appendChild(el("div", { cls: "group-title", text: g[1] }));
      card.appendChild(el("ul", { cls: "items" }, items.map(function (i) {
        var cls = look[i.status] || "todo";
        if (g[0] === "advised" && cls === "bad") cls = "warn";
        return el("li", null, el("span", { cls: "what" }, i.item),
          el("span", { cls: "pill" }, mark(cls), t("s_" + i.status)),
          i.note || i.source ? el("span", { cls: "note" }, i.note || "", /^https:\/\//.test(i.source || "") ?
            [" · ", el("a", { href: i.source, rel: "noopener noreferrer", target: "_blank", text: i.source.replace(/^https:\/\//, "") })] : null) : null);
      })));
    });
    if (co.checked) card.appendChild(el("p", { cls: "small muted", text: t("checked_on", { d: co.checked }) }));
    return s;
  }

  function renderBoard(st) {
    var s = section("board", t("board_title")), card = el("div", { cls: "card" });
    s.appendChild(card);
    var steps = el("div", { cls: "steps" }, st.steps.map(function (x) {
      return el("div", { cls: "step", title: "/" + x.skill }, mark(x.done ? "ok" : "todo"), el("span", { text: t("step_" + x.step) }),
        el("span", { cls: "sr-only", text: " " + t(x.done ? "done" : "not_done") }));
    }));
    card.appendChild(el("div", { cls: "chart-head" }, el("h3", { text: t("so_far") })));
    card.appendChild(el("div", { style: "margin-top:10px" }, steps));
    card.appendChild(el("div", { cls: "chart-head", style: "margin-top:20px" }, el("h3", { text: t("board_vote") })));
    if (!st.board.length) { card.appendChild(empty(t("no_board"), "checker-board")); return s; }
    card.appendChild(el("div", { cls: "board" }, st.board.map(function (m) {
      return el("button", { cls: "member", type: "button", onclick: function () { openDoc(m.doc); } },
        el("div", { cls: "lens", text: t("lens", { l: t("lens_" + m.lens) }) }),
        el("div", { cls: "vote", text: m.vote ? t("vote_" + m.vote) : "?" }),
        el("div", { cls: "score", text: m.score != null ? t("score", { s: dec(m.score, m.score % 1 ? 1 : 0) }) : t("no_score") }));
    })));
    return s;
  }

  function docTitle(d) { var k = "d_" + d.name.replace(/\.md$/, ""); return STR.en[k] ? t(k) : d.title; }

  function renderDocs(st) {
    var s = section("documents", t("docs_title")), card = el("div", { cls: "card" });
    s.appendChild(card);
    if (!st.docs.length) { card.appendChild(empty(t("no_docs"))); return s; }
    var listed = st.docs.some(function (d) { return d.name === currentDoc; });
    if (!currentDoc || (!listed && currentDoc.indexOf("board/") !== 0)) currentDoc = st.docs[0].name;
    var view = el("div", { cls: "md", id: "docview" });
    var list = el("div", { cls: "doclist", role: "tablist" }, st.docs.map(function (d) {
      return el("button", { type: "button", role: "tab", cls: d.name === currentDoc ? "on" : null, "data-doc": d.name,
        onclick: function () { openDoc(d.name); } }, docTitle(d));
    }));
    card.appendChild(el("div", { cls: "docs" }, list, view));
    card.appendChild(el("p", { cls: "small muted", text: t("docs_lang") }));
    later(function () { showDoc(currentDoc); });
    return s;
  }

  function openDoc(name) {
    currentDoc = name;
    document.querySelectorAll(".doclist button").forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-doc") === name); });
    showDoc(name);
    var d = document.getElementById("documents");
    if (d) d.scrollIntoView({ behavior: "smooth" });
  }
  function showDoc(name) {
    var view = document.getElementById("docview");
    if (!view || !name) return;
    var put = function (text) { view.textContent = ""; view.appendChild(markdown(text || "")); };
    if (EXPORTED) return put((state.docs_text || {})[name] || t("doc_gone"));
    if (docCache[name] && docCache[name].v === state.version) return put(docCache[name].text);
    fetch("/api/doc?name=" + encodeURIComponent(name)).then(function (r) { return r.json(); }).then(function (j) {
      docCache[name] = { v: state.version, text: j.text || "" };
      if (currentDoc === name) put(j.text || t("doc_gone"));
    }).catch(function () { put(t("doc_failed")); });
  }

  // ------------------------------------------------------------ markdown (safe: builds nodes, never HTML from the file)

  function inline(text) {
    var out = [], re = /(`[^`]+`)|(\*\*[^*]+\*\*)|(_[^_]+_)|(\*[^*\s][^*]*\*)|(\[[^\]]+\]\((https?:\/\/[^)\s]+)\))|(https?:\/\/[^\s)]+)/g, last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) out.push(document.createTextNode(text.slice(last, m.index)));
      var x = m[0];
      if (m[1]) out.push(el("code", { text: x.slice(1, -1) }));
      else if (m[2]) out.push(el("strong", null, inline(x.slice(2, -2))));
      else if (m[3] || m[4]) out.push(el("em", null, inline(x.slice(1, -1))));
      else if (m[5]) out.push(el("a", { href: m[6], rel: "noopener noreferrer", target: "_blank", text: x.slice(1, x.indexOf("](")) }));
      else out.push(el("a", { href: x, rel: "noopener noreferrer", target: "_blank", text: x }));
      last = m.index + x.length;
    }
    if (last < text.length) out.push(document.createTextNode(text.slice(last)));
    return out;
  }
  function cells(line) { return line.trim().replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); }); }
  function markdown(src) {
    var root = document.createDocumentFragment(), lines = src.replace(/\r/g, "").split("\n"), i = 0;
    while (i < lines.length) {
      var line = lines[i];
      if (/^```/.test(line)) {
        var code = []; i++;
        while (i < lines.length && !/^```/.test(lines[i])) code.push(lines[i++]);
        i++; root.appendChild(el("pre", null, el("code", { text: code.join("\n") }))); continue;
      }
      var hm = /^(#{1,4})\s+(.*)$/.exec(line);
      if (hm) { root.appendChild(el("h" + hm[1].length, null, inline(hm[2]))); i++; continue; }
      if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
        var head = cells(line), body = []; i += 2;
        while (i < lines.length && /^\s*\|/.test(lines[i])) body.push(cells(lines[i++]));
        root.appendChild(el("div", { cls: "scroll" }, el("table", null,
          el("thead", null, el("tr", null, head.map(function (c) { return el("th", null, inline(c)); }))),
          el("tbody", null, body.map(function (r) { return el("tr", null, r.map(function (c) { return el("td", null, inline(c)); })); })))));
        continue;
      }
      if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
        var ordered = /^\s*\d+\./.test(line), list = el(ordered ? "ol" : "ul");
        while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
          var item = lines[i].replace(/^\s*([-*]|\d+\.)\s+/, ""); i++;
          while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) item += " " + lines[i++].trim();
          list.appendChild(el("li", null, inline(item)));
        }
        root.appendChild(list); continue;
      }
      if (/^\s*(---|\*\*\*)\s*$/.test(line)) { root.appendChild(el("hr")); i++; continue; }
      if (!line.trim()) { i++; continue; }
      var para = [line]; i++;
      while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|```|\s*\||\s*([-*]|\d+\.)\s+)/.test(lines[i])) para.push(lines[i++]);
      root.appendChild(el("p", null, inline(para.join(" "))));
    }
    return root;
  }

  // ------------------------------------------------------------ the fixed page parts: header, nav, buttons

  var live = document.getElementById("live"), liveState = "loading";
  function setLive(on, key) { liveState = key; live.classList.toggle("on", on); live.textContent = t(key); }

  var themeBtn = document.getElementById("theme"), langBtn = document.getElementById("lang"), THEMES = ["auto", "light", "dark"];
  var theme = "auto";
  try { theme = localStorage.getItem("checker-theme") || "auto"; } catch (e) { /* storage off */ }

  function applyChrome() {
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach(function (n) { n.textContent = t(n.getAttribute("data-i18n")); });
    if (theme === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", theme);
    themeBtn.textContent = t("theme_" + theme);
    themeBtn.setAttribute("aria-label", t("theme") + ": " + t("theme_" + theme));
    langBtn.textContent = lang === "id" ? "EN" : "ID";
    langBtn.setAttribute("aria-label", t("lang_label") + ": " + (lang === "id" ? "Bahasa Indonesia" : "English"));
    langBtn.setAttribute("title", lang === "id" ? "Switch to English" : "Ganti ke Bahasa Indonesia");
    live.textContent = t(liveState);
  }

  themeBtn.addEventListener("click", function () {
    theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
    try { localStorage.setItem("checker-theme", theme); } catch (e) { /* storage off */ }
    applyChrome();
    if (state) render(state);  // chart colours are read from the theme
  });
  langBtn.addEventListener("click", function () {
    lang = lang === "id" ? "en" : "id";
    try { localStorage.setItem("checker-lang", lang); } catch (e) { /* storage off */ }
    applyChrome();
    if (state) render(state);
  });

  // ------------------------------------------------------------ render and refresh

  var pending = [];
  function later(fn) { pending.push(fn); }

  function render(st) {
    var app = document.getElementById("app"), y = window.scrollY;
    app.textContent = "";
    document.title = st.business + " · " + t("title");
    var brand = document.getElementById("brand");
    brand.textContent = st.business;
    brand.appendChild(el("small", { text: t("brand_sub") }));
    if (!st.exists && !EXPORTED) app.appendChild(el("div", { cls: "error", text: t("no_folder", { d: st.dir }) }));
    (st.errors || []).forEach(function (e) { app.appendChild(el("div", { cls: "error", text: e })); });
    [renderVerdict, renderMonths, renderMoney, renderFixes, renderChannels, renderCustomers, renderCompliance, renderBoard, renderDocs]
      .forEach(function (f) { app.appendChild(f(st)); });
    app.appendChild(el("footer", null, t("footer") + " " + t(EXPORTED ? "footer_export" : "footer_live")));
    var run = pending; pending = [];
    run.forEach(function (fn) { fn(); });
    window.scrollTo(0, y);
  }

  function load() {
    return fetch("/api/state").then(function (r) { return r.json(); }).then(function (st) {
      state = st; render(st); setLive(true, "live");
    });
  }
  function poll() {
    fetch("/api/version").then(function (r) { return r.json(); }).then(function (j) {
      setLive(true, "live");
      if (!state || j.version !== state.version) return load();
    }).catch(function () { setLive(false, "stopped"); });
  }

  if (window.matchMedia) window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () { if (state) render(state); });
  var resizeTimer;
  window.addEventListener("resize", function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(function () { if (state) render(state); }, 150); });

  applyChrome();
  if (EXPORTED) {
    state = JSON.parse(embedded.textContent);
    setLive(false, "exported_copy");
    render(state);
  } else {
    setLive(false, "loading");
    load().catch(function () { setLive(false, "unreachable"); });
    setInterval(poll, 2000);
  }
})();
