"use strict";
// Actual tree module under an isolated DOM adapter; this does not claim browser paint coverage.
const {test}=require("node:test"),assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const treePath=path.join(__dirname,"../../src/eija_studio/resources/web/tree.js");
const source=fs.readFileSync(treePath,"utf8");

function harness({code=source,focusScroll=false}={}) {
  let document;
  const matches=(node,selector)=>{
    const attributes=[...selector.matchAll(/\[([^=\]]+)(?:="([^"]*)")?\]/g)];
    return attributes.length>0&&attributes.every(([,name,value])=>name==="hidden"?node.hidden:value===undefined?node.getAttribute(name)!==null:node.getAttribute(name)===value);
  };
  class Element {
    constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.parentElement=null;this.attributes=new Map();this.dataset={};this.hidden=false;this.textContent="";this.events=new Map();this.scrollTop=0;}
    get tabIndex(){return Number(this.getAttribute("tabindex")??-1);}
    set tabIndex(value){this.setAttribute("tabindex",value);}
    get firstElementChild(){return this.children[0]||null;}
    setAttribute(name,value){this.attributes.set(name,String(value));}
    getAttribute(name){return this.attributes.get(name)??null;}
    append(...nodes){for(const node of nodes){node.parentElement=this;this.children.push(node);}}
    replaceChildren(...nodes){if(this.contains(document.activeElement))document.activeElement=document.body;for(const child of this.children)child.parentElement=null;this.children=[];this.append(...nodes);}
    contains(node){return node===this||this.children.some(child=>child.contains(node));}
    querySelectorAll(selector){const direct=selector.startsWith(":scope > ");if(direct)selector=selector.slice(9);const found=[];for(const child of this.children){if(matches(child,selector))found.push(child);if(!direct)found.push(...child.querySelectorAll(selector));}return found;}
    querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
    closest(selector){for(let node=this;node;node=node.parentElement)if(matches(node,selector))return node;return null;}
    addEventListener(type,listener){const listeners=this.events.get(type)||[];listeners.push(listener);this.events.set(type,listeners);}
    dispatch(type,extra={}){const event={target:this,key:"",defaultPrevented:false,stopped:false,preventDefault(){this.defaultPrevented=true;},stopPropagation(){this.stopped=true;},...extra};for(let node=this;node;node=node.parentElement){for(const listener of node.events.get(type)||[])listener(event);node["on"+type]?.(event);if(event.stopped)break;}return event;}
    focus(options={}){for(let node=this;node;node=node.parentElement)if(node.hidden)return;if(focusScroll&&!options.preventScroll)host.scrollTop=999;document.activeElement=this;this.dispatch("focusin");}
  }
  document={createElement:tag=>new Element(tag),body:new Element("body")};document.activeElement=document.body;
  const host=new Element("div"),root=new Element("div");document.body.append(host);host.append(root);
  const context={module:{exports:{}},document};vm.createContext(context);vm.runInContext(code,context,{filename:treePath});
  const tree=context.module.exports,calls=[];
  const items=()=>root.querySelectorAll('[role="treeitem"]');
  const group=kind=>items().find(node=>node.dataset.kind===kind&&node.getAttribute("aria-expanded")!==null);
  const leaf=(kind,id)=>items().find(node=>node.dataset.kind===kind&&node.dataset.itemId===id);
  const selected=()=>root.querySelectorAll('[aria-selected="true"]');
  const tabstops=()=>root.querySelectorAll('[tabindex="0"]');
  return {tree,root,host,document,calls,items,group,leaf,selected,tabstops,render(data,model,options){tree.render(root,data,model,(kind,item)=>calls.push({kind,id:item.id}),options);},key(node,key){return node.dispatch("keydown",{key});},click(node){return node.dispatch("click");},assertRoving(){assert.equal(tabstops().length,1,"exactly one tree tabstop");assert.equal(tabstops()[0].closest('[role="group"][hidden]'),null,"collapsed descendants cannot be tabstops");}};
}

const data={pack:{id:"pack.with.dots",digest:"same-digest"},language:{terms:[{id:"TERM-A",label:"Alpha"},{id:"TERM-B",label:"Beta"}]},roles:[{id:"ROLE-A"},{id:"ROLE-B"}],laws:[{id:"LAW-A"},{id:"LAW-B"}]};
const model={initial:"DRAFT",states:["DRAFT","READY","DONE"],transitions:[{id:"TR-A",action:"Prepare",from:"DRAFT",to:"READY"},{id:"TR-B",action:"Finish",from:"READY",to:"DONE"},{id:"TR-C",action:"Reopen",from:"DONE",to:"DRAFT"}]};
const kinds=["term","state","transition","role","law"];
const freeze=value=>{if(value&&typeof value==="object"){Object.freeze(value);for(const child of Object.values(value))freeze(child);}return value;};
const snapshot=value=>JSON.parse(JSON.stringify(value));
const isOpen=(h,kind)=>h.group(kind).getAttribute("aria-expanded")==="true";

function assertInitial(h){
  h.render(data,model);
  assert.deepEqual(kinds.filter(kind=>isOpen(h,kind)),[]);
  assert.deepEqual(kinds.map(kind=>h.group(kind).children[0].textContent),["Language (2)","States (3)","Transitions (3)","Roles (2)","Laws (2)"]);
  assert.equal(h.items().filter(node=>node.dataset.itemId!==undefined).length,12,"collapsing groups retains all model leaves");
  for(const kind of kinds)assert.equal(h.group(kind).querySelector(':scope > [role="group"]').hidden,true);
  assert.equal(h.root.getAttribute("role"),"tree");assert.equal(h.root.getAttribute("aria-label"),"Domain explorer");h.assertRoving();
}

function assertExpansionRemembered(h){
  h.render(data,model,{key:"case-A"});h.click(h.group("term").children[0]);h.click(h.group("transition").children[0]);assert.equal(isOpen(h,"transition"),true);h.click(h.group("transition").children[0]);
  h.render(data,model,{key:"case-A"});assert.equal(isOpen(h,"term"),true);assert.equal(isOpen(h,"transition"),false);h.assertRoving();
}

test("initial tree exposes every category and count with all groups deliberately collapsed",()=>assertInitial(harness()));

test("deliberate expansion and collapse survive same-case rerenders",()=>assertExpansionRemembered(harness()));

test("selection, focus, expansion and scroll restore independently for cases sharing one pack",()=>{
  const h=harness();h.render(data,model,{key:"case-A"});h.click(h.group("term").children[0]);h.click(h.leaf("term","TERM-B"));h.key(h.group("transition"),"ArrowRight");h.leaf("transition","TR-B").focus();h.host.scrollTop=183;
  h.render(data,model,{key:"case-B"});assert.equal(h.selected().length,0);assert.equal(isOpen(h,"term"),false);assert.equal(h.document.activeElement,h.group("term"));assert.equal(h.host.scrollTop,0);
  h.key(h.group("state"),"ArrowRight");h.leaf("state","READY").focus();h.click(h.leaf("state","READY"));h.host.scrollTop=41;
  h.render(data,model,{key:"case-A"});assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["TERM-B"]);assert.equal(h.document.activeElement,h.leaf("transition","TR-B"));assert.equal(isOpen(h,"term"),true);assert.equal(isOpen(h,"state"),false);assert.equal(h.host.scrollTop,183);h.assertRoving();
  h.render(data,model,{key:"case-B"});assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["READY"]);assert.equal(h.document.activeElement,h.leaf("state","READY"));assert.equal(isOpen(h,"state"),true);assert.equal(isOpen(h,"term"),false);assert.equal(h.host.scrollTop,41);h.assertRoving();
});

test("explicit selection reconciles on render and a null selection clears only that case",()=>{
  const h=harness();h.render(data,model,{key:"case-A",selection:{kind:"transition",id:"TR-C"}});assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["TR-C"]);
  assert.equal(isOpen(h,"transition"),true);assert.equal(h.leaf("transition","TR-C").closest('[role="group"][hidden]'),null);
  h.render(data,model,{key:"case-B",selection:{kind:"state",id:"DONE"}});assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["DONE"]);
  assert.equal(isOpen(h,"state"),true);assert.equal(isOpen(h,"transition"),false);
  h.render(data,model,{key:"case-A",selection:null});assert.equal(h.selected().length,0);h.render(data,model,{key:"case-B"});assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["DONE"]);h.assertRoving();
});

function assertSelectionDisclosure(h){
  const options={key:"case-A",selection:{kind:"transition",id:"TR-A"}};
  h.render(data,model,options);assert.equal(isOpen(h,"transition"),true,"a newly selected concept must be discoverable");
  h.leaf("transition","TR-A").focus();h.click(h.group("transition").children[0]);h.host.scrollTop=91;
  h.render(data,model,options);assert.equal(isOpen(h,"transition"),false,"the same selection must respect a deliberate collapse");
  assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["TR-A"]);assert.equal(h.document.activeElement,h.group("transition"));assert.equal(h.host.scrollTop,91);h.assertRoving();
  h.render(data,model,{...options,selection:{kind:"transition",id:"TR-B"}});assert.equal(isOpen(h,"transition"),true,"a different selection in the same group reveals it again");
  assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["TR-B"]);assert.equal(h.document.activeElement,h.group("transition"));assert.equal(h.host.scrollTop,91);h.assertRoving();
}

test("new explicit selections reveal their group while unchanged selections preserve a deliberate collapse",()=>assertSelectionDisclosure(harness()));

test("returning to a selected case keeps that case's deliberately collapsed group",()=>{
  const h=harness(),a={key:"case-A",selection:{kind:"transition",id:"TR-A"}},b={key:"case-B",selection:{kind:"state",id:"READY"}};
  h.render(data,model,a);h.click(h.group("transition").children[0]);h.render(data,model,b);assert.equal(isOpen(h,"state"),true);
  h.render(data,model,a);assert.equal(isOpen(h,"transition"),false);assert.deepEqual(h.selected().map(node=>node.dataset.itemId),["TR-A"]);h.assertRoving();
});

test("an unresolved explicit selection never expands an unrelated category",()=>{
  const h=harness();h.render(data,model,{key:"case-A",selection:{kind:"transition",id:"missing"}});assert.deepEqual(kinds.filter(kind=>isOpen(h,kind)),[]);assert.equal(h.selected().length,0);h.assertRoving();
});

test("collapsing a focused descendant moves focus and the sole tabstop to its visible group",()=>{
  const h=harness();h.render(data,model);h.key(h.group("transition"),"ArrowRight");h.leaf("transition","TR-B").focus();h.click(h.group("transition").children[0]);assert.equal(h.document.activeElement,h.group("transition"));assert.equal(h.leaf("transition","TR-B").tabIndex,-1);h.assertRoving();
  h.render(data,model);assert.equal(isOpen(h,"transition"),false);assert.equal(h.document.activeElement,h.group("transition"));h.assertRoving();
});

test("arrows, Home, End and Enter follow the visible tree and select the real item",()=>{
  const h=harness();h.render(data,model);h.group("term").focus();
  assert.equal(h.key(h.document.activeElement,"ArrowDown").defaultPrevented,true);assert.equal(h.document.activeElement,h.group("state"));
  h.key(h.document.activeElement,"ArrowRight");assert.equal(isOpen(h,"state"),true);assert.equal(h.document.activeElement,h.group("state"));h.key(h.document.activeElement,"ArrowRight");assert.equal(h.document.activeElement,h.leaf("state","DRAFT"));
  h.key(h.document.activeElement,"ArrowDown");assert.equal(h.document.activeElement,h.leaf("state","READY"));h.key(h.document.activeElement,"Enter");assert.deepEqual(h.calls,[{kind:"state",id:"READY"}]);
  h.key(h.document.activeElement,"ArrowLeft");assert.equal(h.document.activeElement,h.group("state"));h.key(h.document.activeElement,"ArrowLeft");assert.equal(isOpen(h,"state"),false);h.key(h.document.activeElement,"ArrowUp");assert.equal(h.document.activeElement,h.group("term"));
  h.key(h.document.activeElement,"End");assert.equal(h.document.activeElement,h.group("law"));h.key(h.document.activeElement,"Home");assert.equal(h.document.activeElement,h.group("term"));h.key(h.document.activeElement,"Enter");assert.equal(isOpen(h,"term"),true);h.key(h.document.activeElement," ");assert.equal(isOpen(h,"term"),false);h.assertRoving();
});

test("hiding and showing the tree restores scroll even after a hidden rerender",()=>{
  const h=harness();h.render(data,model,{key:"case-A"});h.host.scrollTop=217;h.tree.setVisible(h.root,false);assert.equal(h.root.hidden,true);h.host.scrollTop=0;
  h.render(data,model,{key:"case-A"});assert.equal(h.host.scrollTop,0);h.tree.setVisible(h.root,true);assert.equal(h.root.hidden,false);assert.equal(h.host.scrollTop,217);
  h.tree.setVisible(h.root,true);assert.equal(h.host.scrollTop,217);h.assertRoving();
});

test("restoring keyboard focus does not overwrite remembered scroll through native focus scrolling",()=>{
  const h=harness({focusScroll:true});h.render(data,model,{key:"case-A"});h.key(h.group("transition"),"ArrowRight");h.leaf("transition","TR-C").focus();h.host.scrollTop=73;
  h.render(data,model,{key:"case-A"});assert.equal(h.document.activeElement,h.leaf("transition","TR-C"));assert.equal(h.host.scrollTop,73,"focus restoration must prevent scrolling or precede scroll restoration");h.assertRoving();
});

test("removed selection and focus fall back to a visible item without leaking to another case",()=>{
  const h=harness();h.render(data,model,{key:"case-A"});h.key(h.group("transition"),"ArrowRight");h.leaf("transition","TR-B").focus();h.click(h.leaf("transition","TR-B"));
  const reduced={...model,transitions:model.transitions.filter(item=>item.id!=="TR-B")};h.render(data,reduced,{key:"case-A"});assert.equal(h.selected().length,0);assert.equal(h.document.activeElement,h.group("term"));h.assertRoving();
  h.render(data,model,{key:"case-B"});assert.equal(h.selected().length,0);assert.equal(h.document.activeElement,h.group("term"));h.assertRoving();
});

test("reveal opens the actual requested ancestor without guessed identifiers or cross-kind matches",()=>{
  const h=harness(),unusual={...data,roles:[{id:"same.id [role]"}],laws:[{id:"same.id [role]"}]};h.render(unusual,model);const before=h.items().map(node=>node.getAttribute("aria-expanded"));
  assert.equal(h.tree.reveal(h.root,"role","missing"),false);assert.deepEqual(h.items().map(node=>node.getAttribute("aria-expanded")),before);assert.equal(h.selected().length,0);
  assert.equal(h.tree.reveal(h.root,"law","same.id [role]"),true);assert.equal(isOpen(h,"law"),true);assert.equal(isOpen(h,"role"),false);assert.deepEqual(h.selected().map(node=>[node.dataset.kind,node.dataset.itemId]),[["law","same.id [role]"]]);assert.deepEqual(h.calls,[]);h.assertRoving();
  h.render(unusual,model);assert.equal(isOpen(h,"law"),true);assert.deepEqual(h.selected().map(node=>node.dataset.kind),["law"]);
});

test("empty groups retain their categories and keyboard navigation remains safe",()=>{
  const h=harness();h.render({pack:{id:"empty"}},{});assert.equal(h.items().length,5);for(const kind of kinds)assert.match(h.group(kind).children[0].textContent,/\(0\)$/);
  h.group("transition").focus();assert.doesNotThrow(()=>h.key(h.document.activeElement,"ArrowRight"));assert.equal(h.document.activeElement,h.group("transition"));h.key(h.document.activeElement,"End");assert.equal(h.document.activeElement,h.group("law"));h.assertRoving();
});

test("rendering, expansion, selection and reveal leave frozen domain and model inputs unchanged",()=>{
  const frozenData=freeze(snapshot(data)),frozenModel=freeze(snapshot(model)),beforeData=snapshot(frozenData),beforeModel=snapshot(frozenModel),h=harness();
  h.render(frozenData,frozenModel);h.click(h.group("term").children[0]);h.click(h.leaf("term","TERM-A"));h.tree.reveal(h.root,"state","DONE");h.render(frozenData,frozenModel);assert.deepEqual(frozenData,beforeData);assert.deepEqual(frozenModel,beforeModel);
});

test("initial-expansion oracle rejects an actual-module mutation that opens every group",()=>{
  const target='expanded(section,state.expanded.get(kind)===true)';assert.equal(source.split(target).length,2,"mutate the actual initial expansion application once");
  assert.throws(()=>assertInitial(harness({code:source.replace(target,'expanded(section,true)')})),assert.AssertionError);
});

test("remembered-expansion oracle rejects an actual-module mutation that discards expansion memory",()=>{
  const target='old.expanded=new Map(';assert.equal(source.split(target).length,2,"mutate the actual remembered expansion assignment once");
  assert.throws(()=>assertExpansionRemembered(harness({code:source.replace(target,'old.discardedExpanded=new Map(')})),assert.AssertionError);
});

test("selection-disclosure oracles reject hidden new selections and repeated forced expansion",()=>{
  const target='if(selectionChanged&&items.some(item=>identifier(kind,item.id)===state.selected))state.expanded.set(kind,true);';assert.equal(source.split(target).length,2);
  assert.throws(()=>assertSelectionDisclosure(harness({code:source.replace(target,"")})),assert.AssertionError);
  const forced=source.replace(target,target.replace("selectionChanged&&",""));
  assert.throws(()=>assertSelectionDisclosure(harness({code:forced})),assert.AssertionError);
});
