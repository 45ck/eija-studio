"use strict";
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),assert=require("node:assert/strict"),test=require("node:test");
const file=process.env.DESIGN_JS||path.resolve(__dirname,"../design.js"),source=fs.readFileSync(file,"utf8");
function application(){
  const views=["model","intent","changes","source","evidence","run","history","edit","connection","factory"],buttons=new Map();
  const nodes=new Map(),focus={value:null},surface={scrollTop:0,querySelectorAll:()=>[]};
  const title={focus:()=>{focus.value="heading";}},returnTarget={dataset:{designFocusKey:"changes:source"},focus:()=>{focus.value="changes:source";}};
  nodes.set("surface",surface);nodes.set("surface-title",title);nodes.set("return-origin",{});
  const document={activeElement:returnTarget,body:{classList:{remove(){}}},querySelectorAll(selector){if(selector==="[data-view]")return [...buttons.values()];if(selector==="[data-design-focus-key]")return [returnTarget];throw Error(`Unexpected selector: ${selector}`);}};
  for(const view of views)buttons.set(view,{dataset:{view},addEventListener(event,handler){this.handler=handler;},click(){document.activeElement=this;this.handler();}});
  const context=vm.createContext({document,$:id=>nodes.get(id),focus,buttons,views,Map,render(){},renderSelection(){},renderContext(){},syncNavigation(){},announce(){}});
  const navigation=source.slice(source.indexOf("function navigate("),source.indexOf("function sourceRoute("));
  const globalBinding=source.split(/\r?\n/).find(line=>line.startsWith('document.querySelectorAll("[data-view]").forEach'));
  const returnBinding=source.split(/\r?\n/).find(line=>line.startsWith('$("return-origin").onclick='));
  assert(globalBinding&&returnBinding,"real navigation handler anchors must exist");
  vm.runInContext(`let caseKey="review",view="changes",origin=null;const scrollState=new Map(),disclosureState=new Map(),caseState=new Map();const surfaces=Object.fromEntries(views.map(v=>[v,{title:v}]));function current(){return {id:"DESIGN-A",revision:8};}function selection(){return caseState.get(caseKey)?.selected||{kind:"transition",id:"TR-SAVE"};}\n${navigation}\n${globalBinding}\n${returnBinding}\nglobalThis.api={navigate,setSelection,state:()=>({view,origin,selected:selection()})};`,context);
  const state=()=>JSON.parse(JSON.stringify(context.api.state()));
  return {state,focus,global:view=>buttons.get(view).click(),contextual:view=>{document.activeElement=returnTarget;context.api.navigate(view);},select:id=>context.api.setSelection({kind:"transition",id}),return:()=>nodes.get("return-origin").onclick()};
}
test("global browsing across all ten surfaces never creates a contextual origin",()=>{
  const app=application();for(const view of ["model","intent","source","evidence","run","history","edit","connection","factory","changes"]){app.global(view);assert.equal(app.state().origin,null,view);}
});
test("ordinary global round-trip then a new Verify investigation returns Verify, not earlier Save",()=>{
  const app=application();for(const view of ["model","intent","source","evidence","run","changes"])app.global(view);
  app.select("TR-VERIFY");app.contextual("source");app.global("evidence");app.return();
  assert.equal(app.state().view,"changes");assert.equal(app.state().selected.id,"TR-VERIFY");assert.equal(app.state().origin,null);
});
test("Source to Evidence keeps the original selection despite deliberate selection at the destination",()=>{
  const app=application();app.select("TR-VERIFY");app.contextual("source");app.select("TR-SAVE");app.contextual("evidence");
  assert.equal(app.state().origin.selected.id,"TR-VERIFY");app.return();assert.equal(app.state().selected.id,"TR-VERIFY");
});
test("global arrival at the origin ends a detour without creating a reverse origin",()=>{
  const app=application();app.contextual("source");app.global("changes");assert.equal(app.state().origin,null);
  app.select("TR-VERIFY");app.contextual("evidence");assert.equal(app.state().origin.view,"changes");assert.equal(app.state().origin.selected.id,"TR-VERIFY");
});
test("explicit return restores the surviving invoking control's focus",()=>{
  const app=application();app.select("TR-VERIFY");app.contextual("source");app.contextual("evidence");app.return();assert.equal(app.focus.value,"changes:source");
});
test("same-view or unknown route does not create or replace a detour",()=>{
  const app=application();app.contextual("changes");assert.equal(app.state().origin,null);app.contextual("source");const before=app.state();app.contextual("no-such-surface");assert.deepEqual(app.state(),before);
});
