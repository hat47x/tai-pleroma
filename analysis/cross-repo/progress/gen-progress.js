const d=require('./product-progress-data.js');
const end=new Date(d.asof);
const out=[];
const sum=[];
for(const r of d.repos){
  const W=r.features.reduce((a,f)=>a+f[2],0);
  const done=r.features.reduce((a,f)=>a+f[2]*f[1]/100,0);
  const pct=done/W*100;
  const weeks=(end-new Date(r.start))/6048e5;
  const pace=done/weeks;
  const rem=W-done;
  r.W=W;r.done=done;r.pct=pct;r.weeks=weeks;r.remWeeks=rem/pace;r.rem=rem;
  sum.push(r);
}
const f=x=>x.toFixed(0);
let md=`# プロダクト機能リストと進捗（${d.asof}時点）\n\n進捗は、各リポジトリの現況文書（status・roadmap・Milestone・Issue/ADR台帳）とコード規模から見積もった値です。**主観を含む推定**であり、機能の重み（規模点）は同一リポジトリ内の相対値です。\n\n## 全体サマリ\n\n| repo | 全体進捗 | 開発期間 | 規模点（完了/全体） | 残りの目安（週） |\n|---|---|---|---|---|\n`;
for(const r of sum) md+=`| ${r.name} | ${f(r.pct)}% | ${r.weeks.toFixed(1)}週 | ${r.done.toFixed(0)} / ${r.W} | ${f(r.remWeeks)}〜${f(r.remWeeks*3)}週 |\n`;
md+=`\n残りの目安は、下限を「これまでの平均ペースがそのまま続く場合」、上限をその3倍としています。未実装領域は設計の不確実性が大きく、初期（土台づくり）より手戻りも多いためです。未実装領域には設計の不確実性が大きいものが含まれるため、上振れ（延びる）側に誤差が出やすい点に注意してください。\n`;
for(const r of sum){
  md+=`\n## ${r.name}\n\n${r.kind}。全体進捗 ${f(r.pct)}%。\n\n| 機能 | 進捗 | 規模点 | 根拠・状態 |\n|---|---|---|---|\n`;
  for(const x of r.features) md+=`| ${x[0]} | ${x[1]}% | ${x[2]} | ${x[3]} |\n`;
}
require('fs').writeFileSync('product-progress.md',md);
require('fs').writeFileSync('product-progress.json',JSON.stringify(sum,null,1));
console.log(sum.map(r=>`${r.id} ${f(r.pct)}% rem=${r.rem.toFixed(0)}pts weeks=${r.weeks.toFixed(1)} remWeeks=${f(r.remWeeks)}`).join('\n'));
