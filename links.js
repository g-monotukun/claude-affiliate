// 広告リンクの置き場所。ASPの管理画面でコピーしたリンクのHTMLを、キーごとに貼り付ける。
// 空のままのキーは、記事上に何も表示されない（提携承認前でもページは壊れない）。
const AFF_LINKS = {
  dmm_ai_camp: ``, // DMM 生成AI CAMP（A8.net）
  xserver: ``,     // エックスサーバー（A8.net）
  conoha_wing: `<a href="https://px.a8.net/svt/ejp?a8mat=4BEH59+8G8IWI+50+5SMXIP" rel="nofollow">
<img border="0" width="336" height="280" alt="" src="https://www21.a8.net/svt/bgt?aid=261015885511&wid=001&eno=01&mid=s00000000018035043000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www14.a8.net/0.gif?a8mat=4BEH59+8G8IWI+50+5SMXIP" alt="">`, // ConoHa WING（A8.net）
  onamae: ``,      // お名前.com（A8.net）
};

document.querySelectorAll(".aff[data-aff]").forEach((el) => {
  const html = AFF_LINKS[el.dataset.aff];
  if (html) el.innerHTML = html;
  else el.remove();
});
