// 広告リンクの置き場所。ASPの管理画面でコピーしたリンクのHTMLを、キーごとに貼り付ける。
// 空のままのキーは、記事上に何も表示されない（提携承認前でもページは壊れない）。
const AFF_LINKS = {
  dmm_ai_camp: ``, // DMM 生成AI CAMP（A8.net）
  xserver: ``,     // エックスサーバー（A8.net）
  conoha_wing: ``, // ConoHa WING（A8.net）
  onamae: ``,      // お名前.com（A8.net）
};

document.querySelectorAll(".aff[data-aff]").forEach((el) => {
  const html = AFF_LINKS[el.dataset.aff];
  if (html) el.innerHTML = html;
  else el.remove();
});
