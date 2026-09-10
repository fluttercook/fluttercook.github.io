// Extra widgets ported from the official Flutter Gallery demo catalog
// (github.com/flutter/gallery / azchohfi/flutter_gallery). Appended to WIDGETS.

const GALLERY_EXTRA = [
  { id:'toggle-buttons', group:'Buttons', title:'Toggle', label:'ToggleButtons',
    desc:'Multi-select segmented control.',
    code:`ToggleButtons(\n  isSelected: const [true, false, false],\n  onPressed: (i) {},\n  children: const [Icon(Icons.format_bold), Icon(Icons.format_italic), Icon(Icons.format_underline)],\n)`,
    render(){
      const wrap = el('div','m3');
      const r = el('div','m3-toggle');
      ['B','I','U'].forEach((t,i)=>{
        const b = btn('m3-toggle-btn'+(i===0?' on':''), t, ()=>{
          r.querySelectorAll('.m3-toggle-btn').forEach(x=>x.classList.remove('on'));
          b.classList.add('on');
        });
        r.appendChild(b);
      });
      wrap.appendChild(r); return wrap;
    } },
  { id:'action-chip', group:'Surfaces', title:'ActionChip', label:'ActionChip',
    desc:'Chip that triggers an action.',
    code:`ActionChip(\n  avatar: const Icon(Icons.alarm),\n  label: const Text('Set alarm'),\n  onPressed: () {},\n)`,
    render(){
      const wrap = el('div','m3');
      const r = el('div','m3-wrap');
      const c = btn('m3-chip on','⏱ Set alarm',()=>{});
      r.appendChild(c); wrap.appendChild(r); return wrap;
    } },
  { id:'choice-chip', group:'Surfaces', title:'ChoiceChip', label:'ChoiceChip',
    desc:'Single-select chip.',
    code:`ChoiceChip(\n  label: const Text('Small'),\n  selected: true,\n  onSelected: (v) {},\n)`,
    render(){
      const wrap = el('div','m3');
      const r = el('div','m3-wrap');
      ['Small','Medium','Large'].forEach((t,i)=>{
        const c = btn('m3-chip'+(i===1?' on':''), t, ()=>{
          r.querySelectorAll('.m3-chip').forEach(x=>x.classList.remove('on'));
          c.classList.add('on');
        });
        r.appendChild(c);
      });
      wrap.appendChild(r); return wrap;
    } },
  { id:'data-table', group:'Layout', title:'DataTable', label:'DataTable',
    desc:'Tabular data with selectable rows.',
    code:`DataTable(\n  columns: const [\n    DataColumn(label: Text('Dessert')),\n    DataColumn(label: Text('Calories'), numeric: true),\n  ],\n  rows: const [\n    DataRow(cells: [DataCell(Text('Frozen yogurt')), DataCell(Text('159'))]),\n    DataRow(cells: [DataCell(Text('Ice cream')), DataCell(Text('237'))]),\n  ],\n)`,
    render(){
      const wrap = el('div','m3');
      const t = el('div','m3-table');
      t.innerHTML = '<div class="m3-tr head"><span>Dessert</span><span>Calories</span></div>'+
        '<div class="m3-tr"><span>Frozen yogurt</span><span>159</span></div>'+
        '<div class="m3-tr"><span>Ice cream</span><span>237</span></div>'+
        '<div class="m3-tr"><span>Eclair</span><span>262</span></div>';
      wrap.appendChild(t); return wrap;
    } },
  { id:'divider', group:'Layout', title:'Divider', label:'Divider',
    desc:'Horizontal and vertical separators.',
    code:`const Divider()\nconst VerticalDivider()`,
    render(){
      const wrap = el('div','m3');
      const a = labelSpan('Item above');
      const d = el('div','m3-hr');
      const b = labelSpan('Item below');
      const r = row();
      const l = labelSpan('Left'); l.style.padding='0 12px';
      const v = el('div','m3-vr');
      const rr = labelSpan('Right'); rr.style.padding='0 12px';
      r.append(l,v,rr);
      wrap.append(a,d,b,r); return wrap;
    } },
  { id:'grid-list', group:'Layout', title:'GridView', label:'GridView.count',
    desc:'Two-dimensional scrolling grid.',
    code:`GridView.count(\n  crossAxisCount: 3,\n  children: List.generate(6, (i) => Card(child: Center(child: Text('$i')))),\n)`,
    render(){
      const wrap = el('div','m3');
      const g = el('div','m3-grid');
      for(let i=1;i<=6;i++){
        const c = el('div','m3-tile'); c.textContent = String(i);
        g.appendChild(c);
      }
      wrap.appendChild(g); return wrap;
    } },
  { id:'bottom-sheet', group:'Surfaces', title:'BottomSheet', label:'showModalBottomSheet',
    desc:'Sheet rising from the bottom edge.',
    code:`showModalBottomSheet<void>(\n  context: context,\n  builder: (context) => SizedBox(\n    height: 200,\n    child: Center(child: Text('Sheet content')),\n  ),\n)`,
    render(){
      const wrap = el('div','m3');
      const s = el('div','m3-sheet');
      const handle = el('div','m3-sheet-handle');
      const body = el('div','m3-sheet-body');
      body.innerHTML = '<strong>Share</strong><div style="margin-top:10px;display:flex;gap:16px;justify-content:center;font-size:20px">✉ ⌘ ☁</div>';
      s.append(handle, body);
      wrap.appendChild(s); return wrap;
    } },
  { id:'banner', group:'Feedback', title:'MaterialBanner', label:'MaterialBanner',
    desc:'In-flow important message.',
    code:`MaterialBanner(\n  content: const Text('Connection lost. Changes will sync later.'),\n  actions: [\n    TextButton(onPressed: () {}, child: const Text('Retry')),\n    TextButton(onPressed: () {}, child: const Text('Dismiss')),\n  ],\n)`,
    render(){
      const wrap = el('div','m3');
      const b = el('div','m3-banner');
      b.innerHTML = '<div>Connection lost. Changes will sync later.</div>'+
        '<div style="margin-top:8px;display:flex;gap:8px;justify-content:flex-end">'+
        '<button class="m3-text" type="button">Retry</button>'+
        '<button class="m3-text" type="button">Dismiss</button></div>';
      wrap.appendChild(b); return wrap;
    } },
  { id:'tooltip', group:'Feedback', title:'Tooltip', label:'Tooltip',
    desc:'Informative label on long-press/hover.',
    code:`Tooltip(\n  message: 'More options',\n  child: IconButton(icon: const Icon(Icons.more_vert), onPressed: () {}),\n)`,
    render(){
      const wrap = el('div','m3');
      const box = el('div','m3-tip-wrap');
      const tip = el('div','m3-tip'); tip.textContent='More options';
      const ic = btn('m3-icon-btn','⋮',()=>{ tip.classList.toggle('show'); });
      box.append(ic, tip);
      wrap.appendChild(box);
      setTimeout(()=>tip.classList.add('show'), 400);
      return wrap;
    } },
  { id:'menu', group:'Surfaces', title:'PopupMenu', label:'PopupMenuButton',
    desc:'Overflow menu anchored to a button.',
    code:`PopupMenuButton<String>(\n  onSelected: (v) {},\n  itemBuilder: (context) => const [\n    PopupMenuItem(value: 'share', child: Text('Share')),\n    PopupMenuItem(value: 'copy', child: Text('Copy link')),\n  ],\n)`,
    render(){
      const wrap = el('div','m3');
      const box = el('div','m3-tip-wrap');
      const menu = el('div','m3-popup');
      menu.innerHTML = '<div>Share</div><div>Copy link</div><div>Settings</div>';
      const ic = btn('m3-icon-btn','⋮',()=>{ menu.classList.toggle('show'); });
      box.append(ic, menu);
      wrap.appendChild(box);
      setTimeout(()=>menu.classList.add('show'), 300);
      return wrap;
    } },
  { id:'nav-drawer', group:'Navigation', title:'Drawer', label:'NavigationDrawer',
    desc:'Side navigation panel.',
    code:`Drawer(\n  child: ListView(children: const [\n    DrawerHeader(child: Text('FlutterCook')),\n    ListTile(leading: Icon(Icons.inbox), title: Text('Inbox')),\n    ListTile(leading: Icon(Icons.star), title: Text('Starred')),\n  ]),\n)`,
    render(){
      const wrap = el('div','m3');
      const d = el('div','m3-drawer');
      d.innerHTML = '<div class="m3-drawer-head">FlutterCook</div>'+
        '<div class="m3-list-item active">📥 Inbox</div>'+
        '<div class="m3-list-item">⭐ Starred</div>'+
        '<div class="m3-list-item">⚙ Settings</div>';
      wrap.appendChild(d); return wrap;
    } },
  { id:'nav-rail', group:'Navigation', title:'NavigationRail', label:'NavigationRail',
    desc:'Compact side rail for adaptive layouts.',
    code:`NavigationRail(\n  selectedIndex: 0,\n  destinations: const [\n    NavigationRailDestination(icon: Icon(Icons.inbox), label: Text('Inbox')),\n    NavigationRailDestination(icon: Icon(Icons.star), label: Text('Star')),\n  ],\n)`,
    render(){
      const wrap = el('div','m3');
      const r = el('div','m3-rail');
      [['⌂','Inbox'],['☆','Star'],['☺','Me']].forEach(([ico,lab],i)=>{
        const b = document.createElement('button'); b.type='button'; b.className=i===0?'active':'';
        b.innerHTML = '<span class="ico">'+ico+'</span><span>'+lab+'</span>';
        b.onclick=()=>{ r.querySelectorAll('button').forEach(x=>x.classList.remove('active')); b.classList.add('active'); };
        r.appendChild(b);
      });
      wrap.appendChild(r); return wrap;
    } },
  { id:'bottom-app-bar', group:'Navigation', title:'BottomAppBar', label:'BottomAppBar',
    desc:'Surface docked at the bottom with actions + FAB.',
    code:`Scaffold(\n  bottomNavigationBar: BottomAppBar(\n    child: Row(children: [\n      IconButton(icon: const Icon(Icons.menu), onPressed: () {}),\n      const Spacer(),\n      IconButton(icon: const Icon(Icons.search), onPressed: () {}),\n    ]),\n  ),\n  floatingActionButton: FloatingActionButton(onPressed: () {}, child: Icon(Icons.add)),\n)`,
    render(){
      const wrap = el('div','m3');
      const bar = el('div','m3-bab');
      bar.innerHTML = '<button class="m3-icon-btn" type="button">☰</button>'+
        '<button class="m3-fab" type="button" style="width:44px;height:44px;font-size:18px">+</button>'+
        '<button class="m3-icon-btn" type="button">⌕</button>';
      wrap.appendChild(bar); return wrap;
    } },
  { id:'range-slider', group:'Inputs', title:'RangeSlider', label:'RangeSlider',
    desc:'Select a numeric range.',
    code:`RangeSlider(\n  values: const RangeValues(20, 70),\n  onChanged: (v) {},\n)`,
    render(){
      const wrap = el('div','m3');
      const box = el('div'); box.style.cssText='position:relative;width:100%;height:28px';
      const track = el('div'); track.style.cssText='position:absolute;top:12px;left:0;right:0;height:4px;background:#e7e0ec;border-radius:2px';
      const fill = el('div'); fill.style.cssText='position:absolute;top:12px;left:20%;width:50%;height:4px;background:#6750a4;border-radius:2px';
      [20,70].forEach(p=>{
        const h = el('div'); h.style.cssText='position:absolute;top:4px;left:'+p+'%;width:20px;height:20px;margin-left:-10px;border-radius:50%;background:#6750a4';
        box.appendChild(h);
      });
      box.append(track, fill);
      wrap.appendChild(box); return wrap;
    } },
  { id:'date-picker', group:'Inputs', title:'DatePicker', label:'showDatePicker',
    desc:'Calendar date selection dialog.',
    code:`showDatePicker(\n  context: context,\n  initialDate: DateTime.now(),\n  firstDate: DateTime(2020),\n  lastDate: DateTime(2030),\n)`,
    render(){
      const wrap = el('div','m3');
      const cal = el('div','m3-cal');
      const head = el('div','m3-cal-head'); head.textContent='September 2026';
      const grid = el('div','m3-cal-grid');
      ['S','M','T','W','T','F','S'].forEach(d=>{ const s=el('span'); s.textContent=d; s.style.color='#49454f'; grid.appendChild(s); });
      for(let i=1;i<=30;i++){
        const s = el('span'); s.textContent=String(i); if(i===10) s.className='on';
        grid.appendChild(s);
      }
      cal.append(head, grid);
      wrap.appendChild(cal); return wrap;
    } },
  { id:'search-bar', group:'Inputs', title:'SearchBar', label:'SearchBar',
    desc:'Material 3 search entry.',
    code:`SearchBar(\n  hintText: 'Search',\n  leading: const Icon(Icons.search),\n  onChanged: (q) {},\n)`,
    render(){
      const wrap = el('div','m3');
      const f = el('div','m3-field'); f.style.borderRadius='28px'; f.style.flexDirection='row'; f.style.alignItems='center'; f.style.gap='10px';
      f.innerHTML = '<span>⌕</span><input placeholder="Search" style="flex:1;border:0;background:transparent;outline:0;font-size:15px" />';
      wrap.appendChild(f); return wrap;
    } },
  { id:'bottom-nav', group:'Navigation', title:'BottomNavigation', label:'BottomNavigationBar',
    desc:'Legacy bottom destination bar with labels.',
    code:`BottomNavigationBar(\n  currentIndex: 0,\n  items: const [\n    BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),\n    BottomNavigationBarItem(icon: Icon(Icons.business), label: 'Business'),\n    BottomNavigationBarItem(icon: Icon(Icons.school), label: 'School'),\n  ],\n)`,
    render(){
      const wrap = el('div','m3');
      const nav = el('div','m3-nav');
      nav.style.borderRadius='0';
      [['⌂','Home'],['▣','Business'],['✎','School']].forEach(([ico,lab],i)=>{
        const b = document.createElement('button'); b.type='button'; b.className=i===0?'active':'';
        b.innerHTML = '<span class="ico">'+ico+'</span>'+lab;
        b.onclick=()=>{ nav.querySelectorAll('button').forEach(x=>x.classList.remove('active')); b.classList.add('active'); };
        nav.appendChild(b);
      });
      wrap.appendChild(nav); return wrap;
    } },
  { id:'cupertino-button', group:'Cupertino', title:'CButton', label:'CupertinoButton',
    desc:'iOS-style button.',
    code:`CupertinoButton(\n  onPressed: () {},\n  child: const Text('Cupertino'),\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const r = row();
      r.append(btn('ios-btn filled','Filled',()=>{}), btn('ios-btn','Plain',()=>{}));
      wrap.appendChild(r); return wrap;
    } },
  { id:'cupertino-alert', group:'Cupertino', title:'CAlert', label:'CupertinoAlertDialog',
    desc:'iOS alert dialog.',
    code:`showCupertinoDialog<void>(\n  context: context,\n  builder: (context) => CupertinoAlertDialog(\n    title: const Text('Discard draft?'),\n    content: const Text('Your changes will be lost.'),\n    actions: [\n      CupertinoDialogAction(child: const Text('Cancel')),\n      CupertinoDialogAction(isDestructiveAction: true, child: const Text('Discard')),\n    ],\n  ),\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const d = el('div','ios-alert');
      d.innerHTML = '<div class="t">Discard draft?</div><div class="c">Your changes will be lost.</div>'+
        '<div class="a"><span>Cancel</span><span class="dest">Discard</span></div>';
      wrap.appendChild(d); return wrap;
    } },
  { id:'cupertino-switch', group:'Cupertino', title:'CSwitch', label:'CupertinoSwitch',
    desc:'iOS toggle switch.',
    code:`CupertinoSwitch(\n  value: true,\n  onChanged: (v) {},\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const r = row();
      const sw = el('div','ios-switch on'); sw.tabIndex=0;
      sw.onclick=()=>sw.classList.toggle('on');
      r.append(labelSpan('Airplane mode'), sw);
      wrap.appendChild(r); return wrap;
    } },
  { id:'cupertino-segmented', group:'Cupertino', title:'Segmented', label:'CupertinoSegmentedControl',
    desc:'iOS segmented control.',
    code:`CupertinoSegmentedControl<int>(\n  children: const {0: Text('Day'), 1: Text('Week'), 2: Text('Month')},\n  onValueChanged: (v) {},\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const s = el('div','ios-seg');
      ['Day','Week','Month'].forEach((t,i)=>{
        const b = document.createElement('button'); b.type='button'; b.textContent=t; if(!i) b.className='on';
        b.onclick=()=>{ s.querySelectorAll('button').forEach(x=>x.classList.remove('on')); b.classList.add('on'); };
        s.appendChild(b);
      });
      wrap.appendChild(s); return wrap;
    } },
  { id:'cupertino-slider', group:'Cupertino', title:'CSlider', label:'CupertinoSlider',
    desc:'iOS slider.',
    code:`CupertinoSlider(\n  value: 0.4,\n  onChanged: (v) {},\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const r = row(); r.style.width='100%';
      const s = document.createElement('input'); s.type='range'; s.min=0; s.max=100; s.value=40; s.className='ios-slider';
      r.appendChild(s); wrap.appendChild(r); return wrap;
    } },
  { id:'cupertino-nav-bar', group:'Cupertino', title:'CNavBar', label:'CupertinoNavigationBar',
    desc:'iOS navigation bar.',
    code:`CupertinoNavigationBar(\n  middle: const Text('Inbox'),\n  trailing: CupertinoButton(padding: EdgeInsets.zero, onPressed: () {}, child: const Icon(CupertinoIcons.add)),\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const bar = el('div','ios-nav');
      bar.innerHTML = '<span style="color:#007aff">Back</span><strong>Inbox</strong><span style="color:#007aff">+</span>';
      wrap.appendChild(bar); return wrap;
    } },
  { id:'cupertino-tab-bar', group:'Cupertino', title:'CTabBar', label:'CupertinoTabBar',
    desc:'iOS tab bar.',
    code:`CupertinoTabBar(\n  items: const [\n    BottomNavigationBarItem(icon: Icon(CupertinoIcons.home), label: 'Home'),\n    BottomNavigationBarItem(icon: Icon(CupertinoIcons.search), label: 'Search'),\n  ],\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const t = el('div','ios-tabs');
      [['⌂','Home'],['⌕','Search'],['☺','Me']].forEach(([ico,lab],i)=>{
        const b = document.createElement('button'); b.type='button'; b.className=i===0?'on':'';
        b.innerHTML = ico+'<small>'+lab+'</small>';
        b.onclick=()=>{ t.querySelectorAll('button').forEach(x=>x.classList.remove('on')); b.classList.add('on'); };
        t.appendChild(b);
      });
      wrap.appendChild(t); return wrap;
    } },
  { id:'cupertino-text-field', group:'Cupertino', title:'CTextField', label:'CupertinoTextField',
    desc:'iOS text field.',
    code:`CupertinoTextField(\n  placeholder: 'Email',\n  padding: EdgeInsets.all(12),\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const f = el('div','ios-field');
      f.innerHTML = '<input placeholder="Email" />';
      wrap.appendChild(f); return wrap;
    } },
  { id:'cupertino-activity', group:'Cupertino', title:'CActivity', label:'CupertinoActivityIndicator',
    desc:'iOS activity spinner.',
    code:`const CupertinoActivityIndicator()`,
    render(){
      const wrap = el('div','m3 ios');
      const r = row();
      const sp = el('div','ios-spin');
      r.appendChild(sp); wrap.appendChild(r); return wrap;
    } },
  { id:'cupertino-action-sheet', group:'Cupertino', title:'CActionSheet', label:'CupertinoActionSheet',
    desc:'iOS action sheet.',
    code:`showCupertinoModalPopup<void>(\n  context: context,\n  builder: (context) => CupertinoActionSheet(\n    title: const Text('Choose'),\n    actions: [\n      CupertinoActionSheetAction(onPressed: () {}, child: const Text('Photo')),\n      CupertinoActionSheetAction(onPressed: () {}, child: const Text('Camera')),\n    ],\n  ),\n)`,
    render(){
      const wrap = el('div','m3 ios');
      const s = el('div','ios-sheet');
      s.innerHTML = '<div class="grp"><div class="title">Choose</div><div>Photo</div><div>Camera</div></div>'+
        '<div class="grp cancel">Cancel</div>';
      wrap.appendChild(s); return wrap;
    } },
];

// CSS for extra widgets
const extraCss = document.createElement('style');
extraCss.textContent = `
.m3-toggle{display:flex;border:1px solid #79747e;border-radius:8px;overflow:hidden}
.m3-toggle-btn{border:0;border-right:1px solid #79747e;background:transparent;padding:10px 16px;cursor:pointer;color:#49454f;font-weight:600}
.m3-toggle-btn:last-child{border-right:0}
.m3-toggle-btn.on{background:#e8def8;color:#4f378b}
.m3-table{background:#fffbfe;border:1px solid #e7e0ec;border-radius:12px;overflow:hidden;font-size:13px;width:100%}
.m3-tr{display:grid;grid-template-columns:1.4fr 1fr;padding:10px 14px;border-bottom:1px solid #e7e0ec}
.m3-tr.head{font-weight:700;color:#49454f;background:#f7f2fa}
.m3-tr:last-child{border-bottom:0}
.m3-hr{height:1px;background:#e7e0ec;margin:10px 0;width:100%}
.m3-vr{width:1px;background:#e7e0ec;align-self:stretch;min-height:24px}
.m3-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;width:100%}
.m3-tile{background:#e8def8;color:#4f378b;border-radius:8px;min-height:56px;display:grid;place-items:center;font-weight:600}
.m3-sheet{background:#fffbfe;border-radius:16px 16px 0 0;box-shadow:0 -4px 16px rgba(0,0,0,.12);padding:8px 0 16px}
.m3-sheet-handle{width:32px;height:4px;border-radius:2px;background:#cac4d0;margin:0 auto 12px}
.m3-sheet-body{padding:0 20px;text-align:center;color:#1c1b1f}
.m3-banner{background:#f7f2fa;border:1px solid #e7e0ec;border-radius:8px;padding:14px 16px;color:#1c1b1f;font-size:13px;line-height:1.4}
.m3-tip-wrap{position:relative;display:inline-flex}
.m3-tip{position:absolute;top:-34px;left:50%;transform:translateX(-50%);background:#322f35;color:#f5eff7;font-size:11px;padding:4px 8px;border-radius:4px;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .15s}
.m3-tip.show{opacity:1}
.m3-popup{position:absolute;top:40px;right:0;background:#fffbfe;border:1px solid #e7e0ec;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.15);min-width:140px;opacity:0;pointer-events:none;transform:translateY(-4px);transition:.15s;z-index:2}
.m3-popup.show{opacity:1;pointer-events:auto;transform:none}
.m3-popup div{padding:10px 14px;font-size:13px;color:#1c1b1f;cursor:pointer}
.m3-popup div:hover{background:#f7f2fa}
.m3-drawer{background:#fffbfe;border:1px solid #e7e0ec;border-radius:0 12px 12px 0;width:200px;overflow:hidden}
.m3-drawer-head{padding:20px 16px;font-weight:700;background:#e8def8;color:#4f378b}
.m3-drawer .m3-list-item{border-bottom:0;cursor:pointer}
.m3-drawer .m3-list-item.active{background:#e8def8;color:#4f378b}
.m3-rail{display:flex;flex-direction:column;gap:4px;background:#f7f2fa;border-radius:12px;padding:12px 8px;width:88px}
.m3-rail button{border:0;background:transparent;display:flex;flex-direction:column;align-items:center;gap:2px;padding:10px 4px;border-radius:16px;cursor:pointer;color:#49454f;font-size:10px}
.m3-rail button.active{background:#d0bcff;color:#1c1b1f;font-weight:600}
.m3-rail .ico{font-size:18px}
.m3-bab{background:#e8def8;display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-radius:0}
.m3-cal{background:#fffbfe;border:1px solid #e7e0ec;border-radius:12px;padding:12px;width:100%}
.m3-cal-head{text-align:center;font-weight:600;margin-bottom:8px;color:#1c1b1f}
.m3-cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;text-align:center;font-size:12px;color:#1c1b1f}
.m3-cal-grid span{padding:6px 0;border-radius:50%;cursor:pointer}
.m3-cal-grid span.on{background:#6750a4;color:#fff}
/* Cupertino */
.m3.ios{color:#000;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.ios-btn{border:0;border-radius:8px;padding:10px 18px;font-size:15px;background:#efeff4;color:#007aff;cursor:pointer}
.ios-btn.filled{background:#007aff;color:#fff}
.ios-alert{background:#f9f9f9ee;border-radius:14px;max-width:270px;overflow:hidden;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.18)}
.ios-alert .t{padding:16px 16px 4px;font-weight:600}
.ios-alert .c{padding:0 16px 14px;font-size:13px;color:#3c3c43}
.ios-alert .a{display:flex;border-top:0.5px solid #3c3c4333}
.ios-alert .a span{flex:1;padding:12px;color:#007aff;cursor:pointer;border-right:0.5px solid #3c3c4333}
.ios-alert .a span:last-child{border-right:0}
.ios-alert .a .dest{color:#ff3b30;font-weight:600}
.ios-switch{width:51px;height:31px;border-radius:16px;background:#e9e9ea;position:relative;cursor:pointer;transition:background .2s}
.ios-switch::after{content:"";position:absolute;top:2px;left:2px;width:27px;height:27px;border-radius:50%;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.2);transition:transform .2s}
.ios-switch.on{background:#34c759}
.ios-switch.on::after{transform:translateX(20px)}
.ios-seg{display:flex;background:#78788033;border-radius:8px;padding:2px}
.ios-seg button{flex:1;border:0;background:transparent;padding:6px 12px;border-radius:7px;font-size:13px;cursor:pointer;color:#000}
.ios-seg button.on{background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12);font-weight:600}
.ios-slider{width:100%;accent-color:#007aff}
.ios-nav{background:#f9f9f9;border-bottom:0.5px solid #3c3c4333;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;font-size:16px}
.ios-tabs{display:flex;background:#f9f9f9;border-top:0.5px solid #3c3c4333}
.ios-tabs button{flex:1;border:0;background:transparent;display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px;font-size:18px;color:#3c3c4399;cursor:pointer}
.ios-tabs button.on{color:#007aff}
.ios-tabs small{font-size:10px}
.ios-field input{width:100%;background:#fff;border:0.5px solid #3c3c4333;border-radius:8px;padding:10px 12px;font-size:15px;outline:0}
.ios-spin{width:28px;height:28px;border-radius:50%;border:3px solid #e5e5ea;border-top-color:#8e8e93;animation:wp-spin 0.8s linear infinite}
.ios-sheet{width:100%}
.ios-sheet .grp{background:#ffffffee;border-radius:12px;overflow:hidden;margin-bottom:8px;text-align:center}
.ios-sheet .grp div{padding:14px;border-bottom:0.5px solid #3c3c4333;color:#007aff;font-size:17px;cursor:pointer}
.ios-sheet .grp div:last-child{border-bottom:0}
.ios-sheet .title{color:#8e8e93;font-size:13px;background:#f9f9f9}
.ios-sheet .cancel{font-weight:600;color:#007aff}
`;
document.head.appendChild(extraCss);
