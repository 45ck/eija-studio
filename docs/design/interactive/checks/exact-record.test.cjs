"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(path.resolve(__dirname,"../design.js"),"utf8");
const start=source.indexOf("function exactRecord("),end=source.indexOf("function field(",start);
assert.ok(start>=0&&end>start,"actual authored raw-record helper exists");
const context={el:(tag,text,className)=>({tag,textContent:text,className,attributes:{},setAttribute(key,value){this.attributes[key]=value;}})};
vm.createContext(context);vm.runInContext(source.slice(start,end),context);
test("raw diagnostic retains exact data while exposing a named native keyboard region",()=>{
  const value=Object.freeze({status:"unknown",actor:"Agent",diagnostic:"<script>inert</script>",refs:Object.freeze(["fixture://exact/reference"])});
  const node=context.exactRecord("Latest attempt identity and diagnostic JSON",value);
  assert.equal(node.tag,"pre");assert.equal(node.tabIndex,0);assert.equal(node.attributes.role,"region");assert.equal(node.attributes["aria-label"],"Latest attempt identity and diagnostic JSON");
  assert.deepEqual(JSON.parse(node.textContent),value);assert.equal(node.className,"exact-record");assert.equal(node.onkeydown,undefined,"native scroll/exit behavior has no custom key trap");
});
test("both authored raw surfaces have distinct accessible names and no generic pre bypass remains",()=>{
  assert.equal((source.match(/el\("pre"/g)||[]).length,1,"only the shared raw-record helper creates authored pre blocks");
  assert.ok(source.includes('exactRecord("Latest attempt identity and diagnostic JSON"'));
  assert.ok(source.includes('exactRecord("Illustrative witness record and assumptions JSON"'));
});
