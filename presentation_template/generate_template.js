// Generic PowerPoint reference only — NO NFL findings; NOT an official Amazon template.
// Requires PptxGenJS 4.0.0. Run: npm install && node generate_template.js
const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'NFL x AWS student preparation';
pptx.title = 'Evidence-first sports analytics — reference deck';
pptx.subject = 'Data-free practice reference. Not a pre-built competition submission.';
pptx.company = 'Independent student project';
pptx.lang = 'en-US';
pptx.theme = {headFontFace:'Aptos Display',bodyFontFace:'Aptos',lang:'en-US'};
const S=pptx.ShapeType;
const C={navy:'172333',deep:'0F1824',orange:'FF9900',white:'FFFFFF',light:'F4F6F8',ink:'202D3A',muted:'64748B',border:'DCE2E8',green:'227E61'};
const W=13.333,H=7.5;
function box(s,x,y,w,h,color){s.addShape(S.rect,{x,y,w,h,line:{color,transparency:100},fill:{color}})}
function txt(s,value,x,y,w,h,size=18,color=C.ink,opt={}){
 s.addText(value,{x,y,w,h,fontFace:'Aptos',fontSize:size,color,bold:!!opt.bold,margin:0,fit:'shrink',breakLine:false,valign:'mid',align:opt.align||'left',charSpacing:opt.charSpacing||0});
}
function head(s,n,principle,title,desc){
 box(s,0,0,W,H,C.light);box(s,0,0,W,.12,C.orange);
 txt(s,String(n).padStart(2,'0')+' / '+principle.toUpperCase(),.70,.47,11,.33,11,C.muted,{bold:true,charSpacing:1});
 txt(s,title,.70,1.03,11.9,.79,31,C.ink,{bold:true});
 txt(s,desc,.70,1.91,11.8,.54,15,C.muted);
 box(s,.70,7.09,11.95,.018,C.border);
 txt(s,'PRACTICE ONLY  •  NOT AN OFFICIAL AMAZON TEMPLATE  •  NO NFL FINDINGS',.70,7.14,11.9,.22,7.3,C.muted);
}
function panel(s,x,y,w,h,title,body,accent=C.orange){
 box(s,x,y,w,h,C.white);box(s,x,y,.065,h,accent);
 txt(s,title,x+.24,y+.26,w-.48,.42,17,C.ink,{bold:true});
 txt(s,body,x+.24,y+.86,w-.5,h-1.06,13,C.muted);
}
{
 const s=pptx.addSlide();box(s,0,0,W,H,C.deep);box(s,.77,.94,.12,5.11,C.orange);
 box(s,1.17,.90,2.32,.39,C.orange);txt(s,'PRACTICE STRUCTURE',1.30,.97,2.08,.21,10,C.deep,{bold:true});
 txt(s,'What changed —\nand who should care?',1.18,1.65,10.6,2.0,42,C.white,{bold:true});
 txt(s,'[One evidence-backed finding created after the challenge begins]',1.19,4.22,10.35,.89,19,'D7E1EC');
 box(s,1.16,6.19,10.95,.016,'485360');
 txt(s,'NFL x AWS  /  data storytelling reference',1.16,6.4,8.1,.32,12,'ABB7C4');
 txt(s,'NOT A SUBMISSION',9.79,6.4,2.32,.28,10,C.orange,{bold:true});
}
{
 const s=pptx.addSlide();head(s,1,'Customer obsession','Start with the decision','Work backwards from someone who will actually use the insight.');
 panel(s,.72,2.62,3.73,3.34,'WHO?','[Pick ONE user]\nCoach / scout / editor / commentator');
 panel(s,4.81,2.62,3.73,3.34,'WHAT IS HARD?','[An unresolved decision]\n[Why established metrics fall short]');
 panel(s,8.90,2.62,3.73,3.34,'WHAT CHANGES?','[Concrete next action]\n[How the user benefits]');
}
{
 const s=pptx.addSlide();head(s,2,'Invent and simplify','One claim. One metric. One comparison.','If this cannot fit in one sentence, simplify the project.');
 box(s,.73,2.55,11.90,1.21,C.navy);
 txt(s,'[Specific claim about an OBSERVABLE football behavior]',1.13,2.78,11.1,.73,24,C.white,{bold:true});
 panel(s,.73,4.18,3.72,1.74,'METRIC','[Definition + unit]');
 panel(s,4.82,4.18,3.72,1.74,'BASELINE','[Fair comparison]');
 panel(s,8.91,4.18,3.72,1.74,'SAMPLE','[How many eligible plays?]');
}
{
 const s=pptx.addSlide();head(s,3,'Dive deep','Make the evidence visible','Your visualization must demonstrate the numerical claim.');
 box(s,.73,2.51,7.86,3.83,C.navy);
 s.addShape(S.rect,{x:1.05,y:2.84,w:7.22,h:3.13,fill:{color:C.navy,transparency:100},line:{color:'8090A0',dash:'dash',width:1.3}});
 txt(s,'[INSERT VERIFIED 2D FIELD REPLAY]',1.49,3.76,6.4,.58,20,C.white,{bold:true,align:'center'});
 txt(s,'Created from the released data during the event',1.47,4.38,6.48,.48,12,'CFD9E3',{align:'center'});
 panel(s,8.90,2.51,3.72,3.83,'PROOF CHECK','• Correct play / player IDs\n• Frames synchronized\n• Units and direction\n• Denominator visible');
}
{
 const s=pptx.addSlide();head(s,4,'Deliver results','Show the mechanism in four steps','Explain the algorithm without saying “we used AI”.');
 [['01','DATA','[Released data fields]'],['02','ALGORITHM','[Actual calculation]'],['03','TEST','[Evidence vs baseline]'],['04','OUTPUT','[Metric + replay]']].forEach((p,i)=>{
  const x=.73+i*3.15;box(s,x,2.60,2.88,2.59,C.white);box(s,x+.23,2.92,.54,.4,C.orange);
  txt(s,p[0],x+.31,2.98,.4,.24,11,C.deep,{bold:true});
  txt(s,p[1],x+.25,3.49,2.36,.45,17,C.ink,{bold:true});
  txt(s,p[2],x+.25,4.17,2.36,.62,12,C.muted);
  if(i!==3)txt(s,'→',x+2.91,3.49,.22,.42,19,C.orange,{bold:true,align:'center'});
 });
 box(s,.73,5.68,11.91,.72,'E8EDF2');
 txt(s,'OPTIONAL LLM  ≠  THE METRIC: explain only verified and auditable results.',1.01,5.84,11.28,.31,13,C.ink,{bold:true});
}
{
 const s=pptx.addSlide();head(s,5,'Earn trust','Prove what works — and what does not','Limitations strengthen the claim when they are specific.');
 panel(s,.73,2.54,5.65,3.39,'WE VERIFIED','[Checks run]\n[Calculation sanity tests]\n[An auditable example]',C.green);
 panel(s,6.96,2.54,5.65,3.39,'WE CANNOT CLAIM','[Unknown context]\n[Small sample bias]\n[Correlation is not causation]','DF714A');
}
{
 const s=pptx.addSlide();head(s,6,'Think big','Translate the result into customer value','Different audiences need decisions, not buzzwords.');
 panel(s,.73,2.54,3.73,3.38,'COACH / SCOUT','[Film review]\n[What player or play to investigate?]');
 panel(s,4.81,2.54,3.73,3.38,'REPORTER','[Defensible story]\n[Sample and comparison]');
 panel(s,8.89,2.54,3.73,3.38,'BROADCAST','[One replay callout]\n[What viewers understand]');
}
{
 const s=pptx.addSlide();box(s,0,0,W,H,C.navy);box(s,0,0,W,.12,C.orange);
 txt(s,'THE DEMO IS THE PROOF',.85,.63,11,.5,13,C.orange,{bold:true,charSpacing:1});
 txt(s,'Show it. Explain it.\nMake the next decision obvious.',.85,1.36,11.5,1.55,33,C.white,{bold:true});
 [['01','PLAY','[One verified case]'],['02','PROOF','[Value, baseline, sample]'],['03','IMPACT','[User action and limitation]']].forEach((p,i)=>{
  const y=3.39+i*.96;box(s,.85,y,.65,.63,C.orange);txt(s,p[0],.94,y+.12,.51,.31,14,C.deep,{bold:true});
  txt(s,p[1],1.82,y,1.42,.47,18,C.white,{bold:true});
  txt(s,p[2],3.55,y,8.15,.47,15,'CBD7E2');
 });
 txt(s,'Data-free rehearsal only. Create competition work in the permitted event window.',.85,6.65,11.65,.31,10,'B9C6D2');
}
pptx.writeFile({fileName:process.argv[2] || 'nfl_aws_evidence_first_template.pptx'});
