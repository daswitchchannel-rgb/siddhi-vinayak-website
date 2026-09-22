const R='https://commons.wikimedia.org/wiki/Special:Redirect/file/';
const materialRefs=[
['Sandstone','Stone • Jali • Jharokha',R+'Jali_sandstone_detail.png'],
['Gwalior Red Stone','Gwalior architectural stone reference',R+'Gwalior_Gopanchal_Parvat_Jain_Archaeological_Site_MP_2021_12_15_162450_07.jpg'],
['Jaisalmer Yellow Stone','Yellow sandstone architecture',R+'Narrow_alleys_of_Jasalmer_fort.jpg'],
['Bansi Paharpur Stone','Heritage sandstone reference',R+'The_Maharajahs_Palace.jpg'],
['Pink Stone','Pink/red sandstone reference',R+'Khalili_Collection_Islamic_Art_mxd_0260.1.jpg'],
['Granite','Natural stone reference',R+'Granite.jpg'],
['Marble','Marble carving reference',R+'Detail_of_Marble_Carving_and_Inlay_-_Mausoleum_-_Taj_Mahal_-_Agra_-_Uttar_Pradesh_-_India_(12650273685).jpg'],
['HDHMR','Interior board — material reference','https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=900&q=80'],
['MDF','CNC decorative panel — material reference','https://images.unsplash.com/photo-1600210492486-724fe5c4e2b3?auto=format&fit=crop&w=900&q=80'],
['Plywood','Interior fabrication — material reference','https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=900&q=80'],
['WPC Board','Decorative board — material reference','https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=900&q=80'],
['PVC Board','Panel work — material reference','https://images.unsplash.com/photo-1615874694520-474822394e73?auto=format&fit=crop&w=900&q=80'],
['Corian / Solid Surface','Seamless surface reference','https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=900&q=80'],
['HPL','Decorative surface reference','https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=900&q=80'],
['Aluminium','CNC metal work reference',R+'Aluminum.svg'],
['Brass / Copper','Metal engraving reference',R+'Brass_plate.png'],
['ACP','Exterior cladding reference','https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=900&q=80'],
['Custom Material','Project-specific fabrication reference',R+'Jami_Masjid_Minar_Base_Detail_Champaner.JPG']
];
document.getElementById('materialGrid').innerHTML=materialRefs.map(x=>'<article class="card material"><img src="'+x[2]+'" alt="'+x[0]+' material reference" loading="lazy"><div class="label">'+x[0]+'</div><div class="sub">'+x[1]+'</div></article>').join('');
const work=[
['Stone Jali','Architectural jali screen',R+'Architectural_Jali_Screen_North_India_early_19th_century_CE%2C_carved_sandstone%2C_Ashmolean_Museum.jpg'],
['Jali Detail','Pierced sandstone detail',R+'Jali_sandstone_detail.png'],
['Geometric Jali','Sidi Saiyed carved stone jali',R+'Sidi_Saiyed_ni_Jali.jpg'],
['Jali Screen','Mughal-style carved jali',R+'Dost_Mohammad_Khan_Tomb%2C_Bhopal_-Jali_03.jpg'],
['Gwalior Stone Carving','Gwalior rock-cut stone reference',R+'0121521_Gopachal_Patthar_ki_Baoli_Jain_monuments%2C_Gwalior_01.jpg'],
['Jaisalmer Stone','Yellow sandstone architectural reference',R+'Narrow_alleys_of_Jasalmer_fort.jpg'],
['Jharokha','Stone jharokha reference',R+'Stone_Jharokha.JPG'],
['Jharokha Detail','Rajput carved jharokha',R+'Jharokha_of_Meherengarh_Fort.jpg'],
['Marble Carving','Marble carving and inlay',R+'Detail_of_Marble_Carving_and_Inlay_-_Mausoleum_-_Taj_Mahal_-_Agra_-_Uttar_Pradesh_-_India_(12650273685).jpg'],
['Marble Gateway','Marble architectural carving',R+'Marble_Carving_-_Gateway_-_Prem_Mandir_-_Bhaktivedanta_Swami_Marg_-_Vrindaban_2013-02-22_4802.JPG'],
['Mehraab / Arch','Historic mehraab reference',R+'The_Roomi_Gate%2C_Lucknow.jpg'],
['Architectural Palace','Red sandstone carved architecture',R+'The_Maharajahs_Palace.jpg']
];
const products=[['Jali','Architectural screens',0],['Jali Detail','Fine carved panels',1],['Geometric Screen','Stone lattice',2],['Carved Jali','Traditional stonework',3],['Stone Relief','Gwalior carving reference',4],['Yellow Stone Work','Jaisalmer-style stonework',5],['Jharokha','Carved window elements',6],['Jharokha Detail','Rajput architectural detail',7],['Marble Panel','Marble carving',8],['Marble Gateway','Decorative marble work',9],['Mehraab / Arch','Architectural arches',10],['Elevation Detail','Heritage elevation reference',11]];
document.getElementById('productGrid').innerHTML=products.map(x=>'<article class="card product"><img src="'+work[x[2]][2]+'" alt="'+x[0]+' — '+x[1]+'" loading="lazy"><div class="label">'+x[0]+'</div><div class="sub">'+x[1]+'</div></article>').join('');
const codes=work.slice(0,8).map((x,i)=>['SV-REF-'+String(i+1).padStart(3,'0'),x[0],x[2]]);
document.getElementById('designGrid').innerHTML=codes.map(x=>'<article class="designCard"><img src="'+x[2]+'" alt="'+x[1]+' reference" loading="lazy"><div class="code">'+x[0]+' · '+x[1]+'</div></article>').join('');
document.getElementById('galleryGrid').innerHTML=work.map(x=>'<article class="galleryItem"><img src="'+x[2]+'" alt="'+x[0]+' — '+x[1]+'" loading="lazy"><div>'+x[0]+' · '+x[1]+'</div></article>').join('');