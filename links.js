// 広告リンクの置き場所。ASPの管理画面でコピーしたリンクのHTMLを、キーごとに貼り付ける。
// 空のままのキーは、記事上に何も表示されない（提携承認前でもページは壊れない）。
const AFF_LINKS = {
  dmm_ai_camp: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+86PL82+5VEK+5YZ75" rel="nofollow">
<img border="0" width="300" height="250" alt="" src="https://www29.a8.net/svt/bgt?aid=261015885495&wid=001&eno=01&mid=s00000027398001003000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BEH59+86PL82+5VEK+5YZ75" alt="">`, // DMM 生成AI CAMP 学び放題（A8.net）※正式名称で記載・略称不可／補助金の記載NG／「稼げる」等の断定・煽り表現NG
  xserver: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8C2HO2+CO4+6PRPD" rel="nofollow">
<img border="0" width="250" height="250" alt="" src="https://www26.a8.net/svt/bgt?aid=261015885504&wid=001&eno=01&mid=s00000001642001128000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BEH59+8C2HO2+CO4+6PRPD" alt="">`,     // エックスサーバー（A8.net）
  conoha_wing: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8G8IWI+50+5SMXIP" rel="nofollow">
<img border="0" width="336" height="280" alt="" src="https://www21.a8.net/svt/bgt?aid=261015885511&wid=001&eno=01&mid=s00000000018035043000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BEH59+8G8IWI+50+5SMXIP" alt="">`, // ConoHa WING（A8.net）
  // テキストリンクを貼ると、商品ボックスのボタンになる（キー名の末尾に _text）
  xserver_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8C2HO2+CO4+61JSI" rel="nofollow">レンタルサーバー エックスサーバー</a>
<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BEH59+8C2HO2+CO4+61JSI" alt="">`,
  conoha_wing_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8G8IWI+50+5SKSCY" rel="nofollow">ConoHa WINGの料金プランを見る</a>
<img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4BEH59+8G8IWI+50+5SKSCY" alt="">`,
  onamae_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+40OCS2+50+2HFY7M" rel="nofollow">お名前.comでドメインを探す</a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BEH59+40OCS2+50+2HFY7M" alt="">`,
  dmm_ai_camp_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+86PL82+5VEK+5YRHE" rel="nofollow">DMM 生成AI CAMP 学び放題</a>
<img border="0" width="1" height="1" src="https://www11.a8.net/0.gif?a8mat=4BEH59+86PL82+5VEK+5YRHE" alt="">`,
  onamae: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+40OCS2+50+2HV61T" rel="nofollow">
<img border="0" width="728" height="90" alt="" src="https://www26.a8.net/svt/bgt?aid=261015885243&wid=001&eno=01&mid=s00000000018015094000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BEH59+40OCS2+50+2HV61T" alt="">`,      // お名前.com（A8.net）
  freee: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+5SZ642+3SPO+9FFFOX" rel="nofollow">
<img border="0" width="300" height="250" alt="" src="https://www24.a8.net/svt/bgt?aid=261016892351&wid=001&eno=01&mid=s00000017718057011000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BEHX8+5SZ642+3SPO+9FFFOX" alt="">`, // freee会計（A8.net）
  freee_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+5SZ642+3SPO+9FKSLE" rel="nofollow">経理初心者向けの会計ソフト【freee会計】</a>
<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BEHX8+5SZ642+3SPO+9FKSLE" alt="">`,
  moneyforward: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+5TKLPU+4JGQ+C4TB5" rel="nofollow">
<img border="0" width="728" height="90" alt="" src="https://www20.a8.net/svt/bgt?aid=261016892352&wid=001&eno=01&mid=s00000021185002038000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BEHX8+5TKLPU+4JGQ+C4TB5" alt="">`, // マネーフォワード クラウド確定申告（A8.net）
  moneyforward_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+5TKLPU+4JGQ+BWVTE" rel="nofollow">無料の確定申告自動化ソフト マネーフォワード クラウド確定申告</a>
<img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4BEHX8+5TKLPU+4JGQ+BWVTE" alt="">`,
  mf_business: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+64AELU+3SPO+C8MP3M" rel="nofollow">個人事業主にとって必要な機能が搭載！【マネーフォワード クラウド】</a>
<img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4BEHX8+64AELU+3SPO+C8MP3M" alt="">`, // マネーフォワード クラウド 個人事業主向け（A8.net・テキスト）
  jetboy: `<a href="https://t.afi-b.com/visit.php?a=F11620Q-f3887103&p=y997255X" rel="nofollow"><img src="https://www.afi-b.com/upload_image/11620-1587337083-3.jpg" width="468" height="60" style="border:none;" alt="JETBOY" /></a><img src="https://t.afi-b.com/lead/F11620Q/y997255X/f3887103" width="1" height="1" style="border:none;" />`, // JETBOY（afb）※社名・商標でのリスティング出稿NG
  jetboy_text: `<a href="https://t.afi-b.com/visit.php?a=F11620Q-V387596Z&p=y997255X" rel="nofollow">JETBOYのプランを見る</a><img src="https://t.afi-b.com/lead/F11620Q/y997255X/V387596Z" width="1" height="1" style="border:none;" />`,
  flexclip: `<a href="https://t.afi-b.com/visit.php?a=6144096-6473112o&p=y997255X" rel="nofollow"><img src="https://www.afi-b.com/upload_image/14409-1679897742-3.png" width="728" height="90" style="border:none;" alt="FlexClip" /></a><img src="https://t.afi-b.com/lead/6144096/y997255X/6473112o" width="1" height="1" style="border:none;" />`, // FlexClip（afb）※PCでの成果のみ。社名・商標でのリスティング出稿NG
  flexclip_text: `<a href="https://t.afi-b.com/visit.php?a=6144096-K473105P&p=y997255X" rel="nofollow">FlexClipを公式サイトで見る</a><img src="https://t.afi-b.com/lead/6144096/y997255X/K473105P" width="1" height="1" style="border:none;" />`,
  airwifi: `<a href="https://t.afi-b.com/visit.php?a=O12638e-R4227311&p=y997255X" rel="nofollow"><img src="https://www.afi-b.com/upload_image/12638-1620613199-3.png" width="320" height="50" style="border:none;" alt="AiR-Wi-Fi" /></a><img src="https://t.afi-b.com/lead/O12638e/y997255X/R4227311" width="1" height="1" style="border:none;" />`, // AiR-Wi-Fi（afb）※社名・商標でのリスティング出稿NG
  airwifi_text: `<a href="https://t.afi-b.com/visit.php?a=O12638e-r422619S&p=y997255X" rel="nofollow">AiR-Wi-Fiの料金プランを見る</a><img src="https://t.afi-b.com/lead/O12638e/y997255X/r422619S" width="1" height="1" style="border:none;" />`,
  value_ai_writer: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEL1L+5GH2EQ+1JUK+1HMIGH" rel="nofollow">
<img border="0" width="350" height="240" alt="" src="https://www22.a8.net/svt/bgt?aid=261020937330&wid=001&eno=01&mid=s00000007238009007000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BEL1L+5GH2EQ+1JUK+1HMIGH" alt="">`, // Value AI Writer byGMO（A8.net）
  value_ai_writer_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEL1L+5GH2EQ+1JUK+1HNDBM" rel="nofollow">Value AI Writerを公式サイトで見る</a>
<img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4BEL1L+5GH2EQ+1JUK+1HNDBM" alt="">`,
  domoai: `<a href="https://t.afi-b.com/visit.php?a=v16143A-8531425i&p=y997255X" rel="nofollow"><img src="https://www.afi-b.com/upload_image/16143-1779861638-3.png" width="350" height="350" style="border:none;" alt="DomoAI リップシンク" /></a><img src="https://t.afi-b.com/lead/v16143A/y997255X/8531425i" width="1" height="1" style="border:none;" />`, // DomoAI（afb）※社名・商標でのリスティング出稿NG／クーポン 7VVTQQZ5（初回購入、月額10%・年額40%OFF）
  domoai_text: `<a href="https://t.afi-b.com/visit.php?a=v16143A-G520373D&p=y997255X" rel="nofollow">DomoAIを公式サイトで見る</a><img src="https://t.afi-b.com/lead/v16143A/y997255X/G520373D" width="1" height="1" style="border:none;" />`,
  filmora: `<a href="https://t.afi-b.com/visit.php?a=A13462Z-A506837F&p=y997255X" rel="nofollow"><img src="https://www.afi-b.com/upload_image/13462-1738089302-3.png" width="600" height="480" style="border:none;" alt="Filmora" /></a><img src="https://t.afi-b.com/lead/A13462Z/y997255X/A506837F" width="1" height="1" style="border:none;" />`, // Wondershare Filmora（afb）※社名・商品名・類似キーワードでのリスティング出稿NG
  filmora_text: `<a href="https://t.afi-b.com/visit.php?a=A13462Z-m453579p&p=y997255X" rel="nofollow">Filmoraの公式ストアを見る</a><img src="https://t.afi-b.com/lead/A13462Z/y997255X/m453579p" width="1" height="1" style="border:none;" />`,
  comu: `<a href="https://px.a8.net/svt/ejp?a8mat=4BGD78+G994FM+5YZG+5ZEMP" rel="nofollow">
<img border="0" width="300" height="250" alt="" src="https://www23.a8.net/svt/bgt?aid=261104084983&wid=001&eno=01&mid=s00000027862001005000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BGD78+G994FM+5YZG+5ZEMP" alt="">`, // Comu AIボイスレコーダー（A8.net）クーポン comu
  miricanvas: `<a href="https://px.a8.net/svt/ejp?a8mat=4BGD79+CI4HE+5EX8+5ZEMP" rel="nofollow">
<img border="0" width="300" height="250" alt="" src="https://www21.a8.net/svt/bgt?aid=261104085021&wid=001&eno=01&mid=s00000025262001005000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BGD79+CI4HE+5EX8+5ZEMP" alt="">`, // MiriCanvas（A8.net）
  miricanvas_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BGD79+CI4HE+5EX8+5YRHE" rel="nofollow">MiriCanvasでデザインを始める</a>
<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BGD79+CI4HE+5EX8+5YRHE" alt="">`,
  comu_text: `<a href="https://px.a8.net/svt/ejp?a8mat=4BGD78+G994FM+5YZG+5YRHE" rel="nofollow">【Comu】</a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BGD78+G994FM+5YZG+5YRHE" alt="">`,
};

document.querySelectorAll("[data-aff]").forEach((el) => {
  const html = AFF_LINKS[el.dataset.aff];
  if (html) el.innerHTML = html;
  else el.remove();
});

// 広告のクリックを、案件のキーと記事ごとに Google アナリティクスへ記録する（GA_ID が未設定なら何もしない）
document.addEventListener("click", (e) => {
  const a = e.target.closest("[data-aff] a");
  if (!a || typeof gtag !== "function") return;
  gtag("event", "aff_click", {
    program: a.closest("[data-aff]").dataset.aff,
    page_path: location.pathname,
    transport_type: "beacon",
  });
});
