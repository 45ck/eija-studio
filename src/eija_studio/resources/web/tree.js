"use strict";
const EijaTree = (() => {
  const contexts = new WeakMap();
  const visibleItems = root => [...root.querySelectorAll('[role="treeitem"]')].filter(node => !node.closest('[role="group"][hidden]'));
  function expanded(item, open) {item.setAttribute("aria-expanded", String(open));item.querySelector(':scope > [role="group"]').hidden=!open;}
  function remember(root, memory) {
    if(memory.key===null||root.hidden)return;
    const old=memory.views.get(memory.key);
    old.expanded=new Map([...root.querySelectorAll('[aria-expanded]')].map(node=>[node.dataset.kind,node.getAttribute("aria-expanded")==="true"]));
    old.focus=root.querySelector('[tabindex="0"]')?.dataset.eijaId;
    old.selected=root.querySelector('[aria-selected="true"]')?.dataset.eijaId;
    old.scroll=root.parentElement?.scrollTop||0;
  }
  function setVisible(root, visible) {
    const memory=contexts.get(root),wasHidden=root.hidden;if(memory&&!wasHidden)remember(root,memory);
    root.hidden=!visible;
    if(visible&&wasHidden&&memory&&root.parentElement)root.parentElement.scrollTop=memory.views.get(memory.key)?.scroll||0;
  }
  function reveal(root, kind, id) {
    const leaf=[...root.querySelectorAll('[role="treeitem"]')].find(node=>node.dataset.kind===kind&&node.dataset.itemId===id);
    if(!leaf)return false;
    const parent=leaf.parentElement.closest('[role="treeitem"]');if(parent)expanded(parent,true);
    for(const node of root.querySelectorAll('[aria-selected]'))node.setAttribute("aria-selected",String(node===leaf));
    return true;
  }
  function render(root, data, model, select, options={}) {
    let memory=contexts.get(root);if(!memory){memory={views:new Map(),key:null};contexts.set(root,memory);}
    const focused=root.contains(document.activeElement),key=options.key||data.pack.digest||data.pack.id;
    const oldFocus=focused&&key===memory.key?document.activeElement.dataset.eijaId:null;
    remember(root,memory);memory.key=key;
    if(!memory.views.has(key))memory.views.set(key,{expanded:new Map(),focus:null,selected:null,scroll:0});
    const state=memory.views.get(key),identifier=(kind,id)=>`${data.pack.id}.${kind}.${id}`;
    const nextSelection=Object.hasOwn(options,"selection")?(options.selection?identifier(options.selection.kind,options.selection.id):null):state.selected;
    const selectionChanged=nextSelection!==state.selected;state.selected=nextSelection;
    root.replaceChildren();root.setAttribute("role","tree");root.setAttribute("aria-label","Domain explorer");
    const groups=[
      ["Language","term",data.language?.terms||[],item=>item.label||item.id],
      ["States","state",(model?.states||[]).map(id=>({id})),item=>item.id],
      ["Transitions","transition",model?.transitions||[],item=>item.action],
      ["Roles","role",data.roles||[],item=>item.id],
      ["Laws","law",data.laws||[],item=>item.id]
    ];
    for(const [title,kind,items,label]of groups){
      if(selectionChanged&&items.some(item=>identifier(kind,item.id)===state.selected))state.expanded.set(kind,true);
      const section=document.createElement("div");section.setAttribute("role","treeitem");section.tabIndex=-1;section.className="tree-group";section.dataset.kind=kind;section.dataset.eijaId=identifier("group",kind);
      const heading=document.createElement("span");heading.textContent=`${title} (${items.length})`;section.append(heading);
      const children=document.createElement("div");children.setAttribute("role","group");
      for(const item of items){
        const leaf=document.createElement("div");leaf.setAttribute("role","treeitem");leaf.tabIndex=-1;leaf.dataset.kind=kind;leaf.dataset.itemId=item.id;leaf.dataset.eijaId=identifier(kind,item.id);leaf.setAttribute("aria-selected",String(leaf.dataset.eijaId===state.selected));leaf.textContent=label(item);leaf.className="tree-leaf";
        const choose=()=>{for(const node of root.querySelectorAll('[aria-selected]'))node.setAttribute("aria-selected",String(node===leaf));state.selected=leaf.dataset.eijaId;select(kind,item);};
        leaf.addEventListener("click",choose);leaf.addEventListener("keydown",event=>{if(["Enter"," "].includes(event.key)){event.preventDefault();event.stopPropagation();choose();}});children.append(leaf);
      }
      section.append(children);root.append(section);expanded(section,state.expanded.get(kind)===true);
      const toggle=()=>{expanded(section,section.getAttribute("aria-expanded")!=="true");if(!children.hidden)return;const tabstop=children.querySelector('[tabindex="0"]');if(tabstop){tabstop.tabIndex=-1;section.tabIndex=0;if(children.contains(document.activeElement))section.focus();}};
      heading.addEventListener("click",toggle);
      section.addEventListener("keydown",event=>{if(event.target===section&&["Enter"," "].includes(event.key)){event.preventDefault();event.stopPropagation();toggle();}});
    }
    const all=[...root.querySelectorAll('[role="treeitem"]')],visible=visibleItems(root),previous=all.find(node=>node.dataset.eijaId===(oldFocus||state.focus));
    const restore=previous&&!visible.includes(previous)?previous.parentElement.closest('[role="treeitem"]'):previous;
    const target=restore||visible[0];if(target)target.tabIndex=0;
    if(!root.hidden&&root.parentElement)root.parentElement.scrollTop=state.scroll;
    if(focused&&!root.hidden)target?.focus({preventScroll:true});
    root.onfocusin=event=>{if(event.target.getAttribute("role")!=="treeitem")return;for(const node of all)node.tabIndex=node===event.target?0:-1;};
    root.onkeydown=event=>{
      const item=event.target.closest('[role="treeitem"]');if(!item)return;
      const visible=visibleItems(root),index=visible.indexOf(item);let next;
      if(event.key==="ArrowDown")next=visible[Math.min(index+1,visible.length-1)];
      if(event.key==="ArrowUp")next=visible[Math.max(0,index-1)];
      if(event.key==="Home")next=visible[0];if(event.key==="End")next=visible[visible.length-1];
      const group=item.querySelector(':scope > [role="group"]');
      if(event.key==="ArrowRight"&&group){if(group.hidden){expanded(item,true);next=item;}else next=group.firstElementChild;}
      if(event.key==="ArrowLeft"){if(group&&!group.hidden){expanded(item,false);next=item;}else next=item.parentElement.closest('[role="treeitem"]');}
      if(next){event.preventDefault();event.stopPropagation();next.focus();}
    };
  }
  return {render,reveal,setVisible};
})();
if(typeof module!=="undefined")module.exports=EijaTree;
