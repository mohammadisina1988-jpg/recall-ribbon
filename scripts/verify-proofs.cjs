// Independent oracle expands individual serials rather than using endpoint events.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const hash=body=>crypto.createHash('sha256').update(body).digest('hex');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,'proofs',name+'.json')));
const canonical=v=>JSON.stringify(v,(_,x)=>x&&!Array.isArray(x)&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const same=(a,b)=>assert.equal(canonical(a),canonical(b));
const expected=JSON.parse(fs.readFileSync(path.join(root,'config/expected.json')));
const lotInputs=JSON.parse(fs.readFileSync(path.join(root,'config/lots.json')));
function oracle(notices){
 const points=new Map();
 for(const notice of notices){
  const scope=notice.scope;
  if(scope.decision!=='ACTIVE')continue;
  for(const [left,right] of scope.spans){
   assert.ok(Number.isInteger(left)&&Number.isInteger(right)&&1<=left&&left<=right&&right<=999999);
   for(let serial=left;serial<=right;serial++){
    if(scope.exceptions.some(([a,b])=>a<=serial&&serial<=b))continue;
    if(!points.has(serial))points.set(serial,new Set());
    points.get(serial).add(notice.document.id);
   }
  }
 }
 const segments=[];
 for(const serial of [...points.keys()].sort((a,b)=>a-b)){
  const notices=[...points.get(serial)].sort(),last=segments.at(-1);
  if(last&&last.end+1===serial&&canonical(last.notices)===canonical(notices))last.end=serial;
  else segments.push({start:serial,end:serial,notices});
 }
 return {segments,points,unresolved:notices.filter(n=>n.scope.decision==='UNKNOWN').map(n=>n.document.id)};
}
const manifest=read('deployment');
assert.equal(manifest.network,'studionet');assert.equal(manifest.chain_id,61999);assert.equal(manifest.exact_source_match,true);
assert.equal(manifest.source_sha256,hash(fs.readFileSync(path.join(root,'contracts/recall_ribbon.py'))));
assert.equal(manifest.fixture_revision,fs.readFileSync(path.join(root,'config/fixture-revision.txt'),'utf8').trim());
assert.equal(manifest.transactions.length,5);
let previous=[];
for(const [index,tx] of manifest.transactions.entries()){
 const receipt=read(tx.label+'-receipt');assert.equal(receipt.hash,tx.hash);
 assert.equal(receipt.status_name||receipt.statusName,'FINALIZED');assert.equal(receipt.result_name,'MAJORITY_AGREE');
 assert.ok(['SUCCESS','FINISHED_WITH_RETURN'].includes(receipt.txExecutionResultName||receipt.consensus_data?.leader_receipt?.[0]?.execution_result));
 const votes=Object.values(receipt.consensus_data.votes);assert.ok(votes.filter(v=>v==='agree').length>votes.length/2);
 if(tx.action==='deploy'){
  assert.equal((receipt.data?.contract_address||receipt.txDataDecoded?.contractAddress).toLowerCase(),manifest.contract_address.toLowerCase());
  continue;
 }
 assert.equal(tx.action,'ingest_notice');assert.equal(receipt.to_address.toLowerCase(),manifest.contract_address.toLowerCase());
 const proof=read(tx.label),state=proof.state,notice=state.notices.at(-1);
 assert.equal(proof.transaction.hash,tx.hash);assert.equal(proof.source_sha256,manifest.source_sha256);assert.equal(proof.contract_address,manifest.contract_address);
 assert.equal(state.publisher,'mohammadisina1988-jpg/recall-ribbon');assert.equal(state.manufacturer,'Northforge');assert.equal(state.model,'NF-20');
 assert.equal(state.notices.length,index);same(state.notices.slice(0,-1),previous);previous=state.notices;
 const body=fs.readFileSync(path.join(root,'notices',tx.label+'.json'));
 same(notice.document,JSON.parse(body));same(notice.scope,expected[tx.label]);
 assert.equal(notice.sha256,hash(body));assert.equal(notice.sha256,manifest.sources[tx.label].sha256);
 assert.equal(notice.url,`https://raw.githubusercontent.com/mohammadisina1988-jpg/recall-ribbon/${manifest.fixture_revision}/notices/${tx.label}.json`);
 assert.ok(notice.document.text.includes(notice.quote));assert.ok(notice.quote.length>=10&&notice.quote.length<=500);
 assert.ok(receipt.data.calldata.readable.includes(notice.url));assert.ok(receipt.data.calldata.readable.includes(notice.sha256));
 const independent=oracle(state.notices);same(state.segments,independent.segments);
 assert.equal(proof.lots.length,lotInputs.length);
 for(const [i,lot] of proof.lots.entries()){
  const [start,end]=lotInputs[i];assert.equal(lot.start,start);assert.equal(lot.end,end);assert.equal(lot.total,end-start+1);
  let count=0;for(let serial=start;serial<=end;serial++)if(independent.points.has(serial))count++;
  assert.equal(lot.known_affected,count);same(lot.unresolved,independent.unresolved);
  same(lot.segments,independent.segments.filter(s=>s.start<=end&&start<=s.end).map(s=>({...s,start:Math.max(start,s.start),end:Math.min(end,s.end)})));
  assert.equal(lot.status,independent.unresolved.length?'REVIEW':count===lot.total?'KNOWN_FULL':count?'KNOWN_PARTIAL':'NO_LISTED_MATCH');
 }
}
console.log('Verified source, deployment, four finalized scope decisions, interval provenance and 24 onchain lot queries.');
