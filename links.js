// 広告リンクの置き場所。ASPの管理画面でコピーしたリンクのHTMLを、キーごとに貼り付ける。
// 空のままのキーは、記事上に何も表示されない（提携承認前でもページは壊れない）。
const AFF_LINKS = {
  dmm_ai_camp: ``, // DMM 生成AI CAMP（A8.net）
  xserver: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8C2HO2+CO4+6PRPD" rel="nofollow">
<img border="0" width="250" height="250" alt="" src="https://www26.a8.net/svt/bgt?aid=261015885504&wid=001&eno=01&mid=s00000001642001128000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BEH59+8C2HO2+CO4+6PRPD" alt="">`,     // エックスサーバー（A8.net）
  conoha_wing: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8G8IWI+50+5SMXIP" rel="nofollow">
<img border="0" width="336" height="280" alt="" src="https://www21.a8.net/svt/bgt?aid=261015885511&wid=001&eno=01&mid=s00000000018035043000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BEH59+8G8IWI+50+5SMXIP" alt="">`, // ConoHa WING（A8.net）
  // テキストリンクを貼ると、商品ボックスのボタンになる（キー名の末尾に _text）
  xserver_text: ``,
  conoha_wing_text: ``,
  onamae_text: ``,
  dmm_ai_camp_text: ``,
  onamae: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+40OCS2+50+2HV61T" rel="nofollow">
<img border="0" width="728" height="90" alt="" src="https://www26.a8.net/svt/bgt?aid=261015885243&wid=001&eno=01&mid=s00000000018015094000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BEH59+40OCS2+50+2HV61T" alt="">`,      // お名前.com（A8.net）
  freee: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+5SZ642+3SPO+9FFFOX" rel="nofollow">
<img border="0" width="300" height="250" alt="" src="https://www24.a8.net/svt/bgt?aid=261016892351&wid=001&eno=01&mid=s00000017718057011000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BEHX8+5SZ642+3SPO+9FFFOX" alt="">`, // freee会計（A8.net）
  freee_text: ``,
  moneyforward: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+5TKLPU+4JGQ+C4TB5" rel="nofollow">
<img border="0" width="728" height="90" alt="" src="https://www20.a8.net/svt/bgt?aid=261016892352&wid=001&eno=01&mid=s00000021185002038000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BEHX8+5TKLPU+4JGQ+C4TB5" alt="">`, // マネーフォワード クラウド確定申告（A8.net）
  moneyforward_text: ``,
  mf_business: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEHX8+64AELU+3SPO+C8MP3M" rel="nofollow">個人事業主にとって必要な機能が搭載！【マネーフォワード クラウド】</a>
<img border="0" width="1" height="1" src="https://www17.a8.net/0.gif?a8mat=4BEHX8+64AELU+3SPO+C8MP3M" alt="">`, // マネーフォワード クラウド 個人事業主向け（A8.net・テキスト）
};

document.querySelectorAll("[data-aff]").forEach((el) => {
  const html = AFF_LINKS[el.dataset.aff];
  if (html) el.innerHTML = html;
  else el.remove();
});
