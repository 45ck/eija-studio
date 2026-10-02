"use strict";
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),assert=require("node:assert/strict"),test=require("node:test");
const source=fs.readFileSync(process.env.DESIGN_JS||path.resolve(__dirname,"../design.js"),"utf8");
function app(){
  class Element{
    constructor(tag){this.tag=tag;this.children=[];this.events={};this.attributes={};this.isConnected=true;}
    append(...nodes){this.children.push(...nodes);}addEventListener(name,fn){this.events[name]=fn;}setAttribute(name,value){this.attributes[name]=value;}
    showModal(){this.open=true;}close(){this.open=false;}focus(){this.focused=true;}
  }
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element("div"));return nodes.get(id);};
  const calls=[],invoker=new Element("button"),context={document:{activeElement:invoker},$:get,el:(tag,text,className)=>Object.assign(new Element(tag),{textContent:text,className}),render(){},renderSelection(){},renderContext(){},announce(){},frameComparison:(_host,controller)=>controller,EijaCompare:{render:(_host,data,options)=>{calls.push(JSON.parse(JSON.stringify({data,options})));return {destroy(){}};}}};
  vm.createContext(context);
  for(const[start,end]of [["const copy =","function button("],["function button(","function setState("],["function setSelection(","function sourceRoute("],["const editVariants=","function renderEvidence("]]){
    const from=source.indexOf(start),to=source.indexOf(end,from);assert.ok(from>=0&&to>from,start);vm.runInContext(source.slice(from,to),context);
  }
  vm.runInContext('caseState.set("review",{selected:{kind:"transition",id:"TR-SAVE"},prompt:"Preserve request A"});caseState.set("missing",{selected:{kind:"transition",id:"TR-SAVE"},prompt:"Preserve request B"});globalThis.api={enter:key=>{caseKey=key;view="edit";},select:id=>setSelection({kind:"transition",id}),snapshot:()=>({selected:selection(),source:selectedSource(),caseData:current(),all:cases,stored:[...caseState]}),renderEdit,openPreview,closePreview};',context);
  const all=root=>[root,...root.children.flatMap(all)];
  return {calls,invoker,get,enter:key=>context.api.enter(key),select:id=>context.api.select(id),snapshot:()=>JSON.parse(JSON.stringify(context.api.snapshot())),choose:key=>{const root=new Element("section");context.api.renderEdit(root);const select=all(root).find(node=>node.id==="edit-kind");assert.ok(select,"real prepared-example selector rendered");select.value=key;select.events.change();},open:()=>context.api.openPreview(),close:()=>context.api.closePreview()};
}
test("prepared Verify example and preview closure preserve parked case A Save and exact source context",()=>{
  const a=app();a.enter("review");a.select("TR-SAVE");const before=a.snapshot();
  a.choose("source");a.open();assert.equal(a.calls.at(-1).options.state.selected.id,"TR-VERIFY","preview uses its own selected example");assert.equal(a.calls.at(-1).data.case.id,"DESIGN-UNSUBMITTED");
  a.close();assert.deepEqual(a.snapshot(),before,"choosing/closing a prepared example must preserve parked case and source");assert.equal(a.snapshot().source.name,"Studio.save");assert.equal(a.invoker.focused,true);
});
test("independent choices across cases A and B never rewrite either stored selection or unmapped source",()=>{
  const a=app();a.enter("review");a.select("TR-VERIFY");const beforeA=a.snapshot();a.choose("role");a.open();a.close();assert.deepEqual(a.snapshot(),beforeA);
  a.enter("missing");a.select("TR-SAVE");const beforeB=a.snapshot();assert.equal(beforeB.source,null);a.choose("guards");a.open();a.close();assert.deepEqual(a.snapshot(),beforeB);
  a.enter("review");assert.deepEqual(a.snapshot(),beforeA);assert.equal(a.snapshot().source.name,"Studio.verify");a.enter("missing");assert.deepEqual(a.snapshot(),beforeB);
});
test("all prepared variants select only their independent preview item and preserve case snapshots",()=>{
  const a=app();a.enter("review");a.select("TR-SAVE");const before=a.snapshot();
  for(const[key,id]of [["role","TR-SAVE"],["source","TR-VERIFY"],["target","TR-SAVE"],["guards","TR-VERIFY"]]){a.choose(key);a.open();assert.equal(a.calls.at(-1).options.state.selected.id,id);a.close();assert.deepEqual(a.snapshot(),before,key);}
});
