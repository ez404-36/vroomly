def parse_vehicle_generation_prompt(html: str):
    return """
Ты занимаешься преобразованием содержимого HTML-документа в JSON-формат.
Содержимое представляет собое описание одного поколения конкретной марки и модели автомобиля.
Внутри поколения бывает множество различных комплектаций.
Твои задачи:
1) Определить поколение
2) Определить все модификации данного поколения
3) Предоставить структурированный вывод в формате JSON

## Пример
Исходный HTML:
```html
<article itemprop="articleBody">
<div class="afigure-title">  
	<div class="title-cont"><h1 class="white" itemprop="headline">Kia Sorento Prime</h1>
	<span style="display:none" itemprop="description">Технические характеристики автомобиля Kia Sorento Prime (UM) с пробегом, надежность, ресурс, отзывы, проблемы и расход топлива.</span> 
	<div class="author">
<div itemprop="author" itemscope="" itemtype="https://schema.org/Person">  <meta itemprop="name" content="Андрей Малыхин"><p>Автор:  <a href="https://otoba.ru/info/politika-konfidencialnosti.html#author" target="_blank" rel="noopener">Андрей Малыхин</a></p></div>
</div> 
 	</div>
	<meta itemprop="datePublished" content="2021-03-20T20:52:20.000Z">
	<meta itemprop="dateModified" content="2025-04-14T12:56:00.000Z">			
 <figure class="top-img" itemprop="image" itemscope="" itemtype="https://schema.org/ImageObject">
		<meta itemprop="width" content="900"><meta itemprop="height" content="305">
<picture>
	<source srcset="img/sorento/3/kia-sorento-prime-small.jpg" media="(max-width: 400px)" type="image/jpeg">		
	<source srcset="img/sorento/3/kia-sorento-prime-middle.jpg" media="(max-width: 660px)" type="image/jpeg">
	<img itemprop="url image" src="img/sorento/3/kia-sorento-prime.jpg" width="900" height="305" class="img-b" alt="Кроссовер Kia Sorento Prime (UM)"> 
</picture></figure>	

</div><div class="clear"></div>

<nav class="br-cr"><ul itemscope="" itemtype="https://schema.org/BreadcrumbList">
		<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"> <a href="https://otoba.ru/auto/catalog.html" itemprop="item"><span itemprop="name">Авто</span></a><meta itemprop="position" content="1"></li>	 	 
 
 	
		<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"><a href="https://otoba.ru/auto/kia.html" itemprop="item"><span itemprop="name">Киа</span></a><meta itemprop="position" content="2"></li>	 
 
 
		<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"> <span itemprop="name">Соренто Прайм</span> <meta itemprop="position" content="3"></li>	
	</ul>
</nav>
 
<div class="clear"></div>
  
   
<div class="content">   

<p>Kia Sorento 3-го поколения или Prime в кузове UM производился компанией с 2014 по 2020 годы на заводах в Южной Корее, США, Малайзии и Пакистане, а нашу версию собирали на Автоторе. Существовал аналогичный по всем узлам и агрегатам кроссовер <a href="https://otoba.ru/auto/hyundai/santa-fe-3.html" class="lk">Hyundai Santa Fe в кузове DM</a>.</p>
  
<p>Линейка Sorento: 
<a href="https://otoba.ru/auto/kia/sorento-1.html" class="ssylka">BL&nbsp;(2002&nbsp;‑&nbsp;2009)</a>, 
<a href="https://otoba.ru/auto/kia/sorento-2.html" class="ssylka">XM&nbsp;(2009&nbsp;‑&nbsp;2019)</a> и 
<a href="https://otoba.ru/auto/kia/sorento-4.html" class="ssylka">MQ4&nbsp;(2020&nbsp;‑&nbsp;н.в.)</a>. 
</p>
 
</div> 
	 
<div class="clear"></div>
 
<div class="content"><div class="recl" style="max-height: 300px;margin: 1em auto;text-align: center; display: block; clear: both;">
 
 <!-- Yandex.RTB R-A-1578237-6 -->
<div id="yandex_rtb_R-A-1578237-6" style="width:100%;max-width:850px;max-height: 300px;"><div style="width: 100%;"></div></div>
<script>window.yaContextCb.push(()=>{
  Ya.Context.AdvManager.render({
    renderTo: 'yandex_rtb_R-A-1578237-6',
    blockId: 'R-A-1578237-6'
  })
})</script>
 
</div></div> 

<div class="clear"></div> 

 
<div class="soderzhanie" itemscope="" itemtype="https://schema.org/ItemList"><div class="title-sod">Содержание:</div><div class="clear"></div> 
<ul class="sod-item">
<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"><a itemprop="url" href="#modifikacii"><span itemprop="name"><i class="auto-sod auto-sod-opisanie"></i>Модификации</span></a><meta itemprop="position" content="1"></li>		
<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"><a itemprop="url" href="#tth"><span itemprop="name"><i class="auto-sod auto-sod-tth"></i>ТТХ</span></a><meta itemprop="position" content="2"></li>	
<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"><a itemprop="url" href="#problemy"><span itemprop="name"><i class="auto-sod auto-sod-polomki"></i>Поломки</span></a><meta itemprop="position" content="3"></li>	
<li itemprop="itemListElement" itemscope="" itemtype="https://schema.org/ListItem"><a itemprop="url" href="#cena"><span itemprop="name"><i class="auto-sod auto-sod-cena"></i>Цена</span></a><meta itemprop="position" content="4"></li>	 
</ul>
</div> 
 						 
  
 
<div class="clear"></div>
 
<!-- MODIFIKACII -->	
<a id="modifikacii"></a> 
<div class="clear"></div> 
   
<section><div class="post-title-engine"><div class="post-title-engine_body">
<div class="title-icon"><i class="auto-rubr auto-rubr-opisanie"></i></div><h2 class="cont-title-dop">Модификации Киа Соренто Прайм (UM)</h2>
 </div></div><div class="clear"></div>
<div class="content">
 
<p>Кроссовер до рестайлинга продавали с 2014 по 2017 год, а на нашем рынке с 2015 по 2018 год.</p>
   
<div class="cntimg">
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/kuzov/kia-sorento-prime-speredi.jpg" loading="lazy" width="600" height="400" alt="Кроссовер Киа Соренто Прайм UM до рестайлинга вид спереди" itemprop="contentUrl">
</figure>
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/kuzov/kia-sorento-prime-szadi.jpg" loading="lazy" width="600" height="400" alt="Внедорожник Kia Sorento Prime UM дорестайлинговая версия вид сзади" itemprop="contentUrl">
</figure> 
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/salon/kia-sorento-prime-interior.jpg" loading="lazy" width="600" height="400" alt="Кроссовер Киа Соренто Прайм UM до обновления интерьер" itemprop="contentUrl">
</figure>
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/salon/kia-sorento-prime-salon.jpg" loading="lazy" width="600" height="400" alt="Внедорожник Kia Sorento Prime UM дорестайлинговая модификация салон" itemprop="contentUrl">
</figure> 
</div> 
 
<div class="clear"></div><br>
 
<p>Сперва предлагали только дизель, затем появился агрегат V6, а в 2017 году двигатель 2.4 GDi:</p>
 
<div class="tabl-modif-title">Полноприводные версии</div>  
<div class="tabl-modif-title-sb">Бензиновые модификации</div> 
<div class="tabl-modif">
 <table class="tabl-modif-body-1">  
<tbody><tr><td>2.4 л <a href="https://otoba.ru/dvigatel/hyundai/g4kj.html" class="lk">G4KJ</a> 188 л.с. 241 Нм и 6‑акпп <a href="https://otoba.ru/transmissii/hyundai-kia/a6mf2.html" class="lk">A6MF2</a></td></tr>
 </tbody></table>

<table class="tabl-modif-body-2">  
<tbody><tr><td>3.3 л <a href="https://otoba.ru/dvigatel/hyundai/g6df.html" class="lk">G6DF</a> 250 л.с. 318 Нм и 6‑акпп <a href="https://otoba.ru/transmissii/hyundai-kia/a6lf1.html" class="lk">A6LF1</a></td></tr>
</tbody></table>
</div> 
 
<div class="clear"></div> 
 
<div class="tabl-modif-title-sb">Дизельные модификации</div> 
<div class="tabl-modif">
 <table class="tabl-modif-body-1">  
 <tbody><tr><td>2.2 л <a href="https://otoba.ru/dvigatel/hyundai/d4hb.html" class="lk">D4HB</a> 200 л.с. 441 Нм и 6‑акпп <a href="https://otoba.ru/transmissii/hyundai-kia/a6lf3.html" class="lk">A6LF3</a></td></tr>
 </tbody></table>

<table class="tabl-modif-body-2">  
<tbody><tr class="tab-and"><td>&nbsp;</td></tr>
</tbody></table>
</div> 
 
<p>На других рынках устанавливался 2.4-литровый <a href="https://otoba.ru/dvigatel/hyundai/g4ke.html" class="lk">мотор G4KE</a> и 3.3-литровый <a href="https://otoba.ru/dvigatel/hyundai/g6dh.html" class="lk">GDi агрегат G6DH</a>.</p>
  
<div class="clear"></div><br>
 
 
<div class="lin"></div> 

<p>Этот кроссовер после рестайлинга предлагался с 2017 по 2020 год, а у нас с 2018 по 2020 годы.</p>
   
<div class="cntimg">
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/kuzov/kia-sorento-prime-rest-speredi.jpg" loading="lazy" width="600" height="400" alt="Кроссовер Киа Соренто Прайм UM рестайлинг вид спереди" itemprop="contentUrl">
</figure>
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/kuzov/kia-sorento-prime-rest-szadi.jpg" loading="lazy" width="600" height="400" alt="Внедорожник Kia Sorento Prime UM рестайлинговая версия вид сзади" itemprop="contentUrl">
</figure> 
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/salon/kia-sorento-prime-rest-interior.jpg" loading="lazy" width="600" height="400" alt="Кроссовер Киа Соренто Прайм UM после обновления интерьер" itemprop="contentUrl">
</figure>
<figure class="img-dv" itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="400">
	<img src="img/sorento/3/salon/kia-sorento-prime-rest-salon.jpg" loading="lazy" width="600" height="400" alt="Внедорожник Kia Sorento Prime UM рестайлинговая модификация салон" itemprop="contentUrl">
</figure> 
</div> 
 
<div class="clear"></div><br>
 
<p>При обновлении кроссовера сменился двигатель V6 и появился новый 8-ступенчатый автомат:</p>
 
<div class="tabl-modif-title">Переднеприводные версии</div>  
<div class="tabl-modif-title-sb">Бензиновые модификации</div> 
<div class="tabl-modif">
 <table class="tabl-modif-body-1">  
<tbody><tr><td>2.4 л <a href="https://otoba.ru/dvigatel/hyundai/g4kj.html" class="lk">G4KJ</a> 188 л.с. 241 Нм и 6‑акпп <a href="https://otoba.ru/transmissii/hyundai-kia/a6mf2.html" class="lk">A6MF2</a></td></tr>
 </tbody></table>

<table class="tabl-modif-body-2">  
<tbody><tr class="tab-and"><td>&nbsp;</td></tr> 
</tbody></table>
</div> 
 
<div class="clear"></div><br>
  
<div class="tabl-modif-title">Полноприводные версии</div>  
<div class="tabl-modif-title-sb">Бензиновые модификации</div> 
<div class="tabl-modif">
 <table class="tabl-modif-body-1">  
<tbody><tr><td>2.4 л <a href="https://otoba.ru/dvigatel/hyundai/g4kj.html" class="lk">G4KJ</a> 188 л.с. 241 Нм и 6‑мкпп <a href="https://otoba.ru/transmissii/hyundai-kia/a6mf2.html" class="lk">A6MF2</a></td></tr>
</tbody></table>

<table class="tabl-modif-body-2">  
<tbody><tr><td>3.5 л <a href="https://otoba.ru/dvigatel/hyundai/g6dc.html" class="lk">G6DC</a> 250 л.с. 336 Нм и 8‑акпп <a href="https://otoba.ru/transmissii/hyundai-kia/a8lf1.html" class="lk">A8LF1</a></td></tr>
</tbody></table>
</div> 
  
<div class="clear"></div> 
  
<div class="tabl-modif-title-sb">Дизельные модификации</div> 
<div class="tabl-modif">
 <table class="tabl-modif-body-1">  
<tbody><tr><td>2.2 л <a href="https://otoba.ru/dvigatel/hyundai/d4hb.html" class="lk">D4HB</a> 200 л.с. 441 Нм и 8‑акпп <a href="https://otoba.ru/transmissii/hyundai-kia/a8lf2.html" class="lk">A8LF2</a></td></tr>
 </tbody></table>

<table class="tabl-modif-body-2">  
<tbody><tr class="tab-and"><td>&nbsp;</td></tr> 
</tbody></table>
</div> 
 
<div class="clear"></div> 
 
<p>На других рынках очень часто встречался 2.0-литровый <a href="https://otoba.ru/dvigatel/hyundai/g4kh.html" class="lk">турбомотор с прямым впрыском G4KH</a>.</p>
  
<div class="clear"></div><br>
 
 
<div class="lin"></div> 
 
<!--USEFUL LINKS--> 
<div class="box-pol-links pol-links"><span>Полезные материалы</span><div class="pol-links-text">

<img src="img/sorento/pol-links/manual-kia-sorento-prime.jpg" loading="lazy" width="200" height="150" alt="Мануал о Киа Sorento Prime">
<i>MANUAL</i>
<p>Русскоязычный мануал Kia Sorento 3 <a href="https://krutilvertel.com/catalogue/kia/ebook-kia-sorento-prime?affiliate=61fa4cb30b901" target="_blank" rel="nofollow noopener">выложен тут</a></p>

<div class="clear"></div><br>

<img src="../servis/pol-links/info-drive2-ru.jpg" loading="lazy" width="200" height="150" alt="Инфо drive2-ru">
<i>INFO</i>
<p>Много полезной информации собрано <a href="https://www.drive2.ru/l/508432319699222828/" target="_blank" rel="nofollow noopener noreferrer">на Драйв 2</a></p>
 
</div></div>
<!--USEFUL LINKS-->  
 
<div class="clear"></div><br>
 
<div class="vid-object">
<p class="description">Обзор Киа Соренто 2015 года от МегаРетр</p>	
<div class="vid"> 
<img src="https://img.youtube.com/vi/REGZXCh_9g8/hqdefault.jpg" loading="lazy" width="850" height="450" alt="2015 Kia Sorento Prime. Обзор (интерьер, экстерьер, двигатель)">
<iframe width="850" height="450" src="https://www.youtube.com/embed/REGZXCh_9g8" srcdoc="&lt;style&gt;*{padding:0;margin:0;overflow:hidden} img,span{position:absolute;width:100%;top:0;bottom:0;margin:auto} span{height:1.5em;text-align:center;font:6em/1.5 sans-serif;color:white;text-shadow:0 0 .5em #000; }&lt;/style&gt;
  &lt;a href=https://www.youtube.com/embed/REGZXCh_9g8?autoplay=1&gt;
  &lt;img src=https://img.youtube.com/vi/REGZXCh_9g8/hqdefault.jpg  loading='lazy' alt='2015 Kia Sorento Prime. Обзор (интерьер, экстерьер, двигатель)'&gt;&lt;span&gt;►&lt;/span&gt;&lt;/a&gt;" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" title="2015 Kia Sorento Prime. Обзор (интерьер, экстерьер, двигатель)"></iframe>
</div></div>

</div></section>     
<!-- MODIFIKACII -->

 <div class="clear"></div>
     
<!-- TTH -->	
<a id="tth"></a>  
<div class="clear"></div> 
 
<!--noindex--><div class="content">
 
<div class="clear"></div><br>
 
<div class="block-reclama"><div class="banner-ferio">
 
<div class="slogan-ferio">
<p class="zagl">Найдем любой мотор / кпп</p>
<div class="slogan-ferio-osn">
<div class="banner-logo-ferio"><img src="https://otoba.ru/assets/reclama/company/ferio/img/feriologo.png" loading="lazy" width="681" height="309" alt="Логотип Ферио"><p> - 20 лет находим запчасти для Вас</p></div> 

<div class="clear"></div> 
 
<p>• без посредников</p>
<p>• только проверенные авторазборки</p>
<p>• снимаем ошибку подбора</p>

<a class="flare-button-ferio" href="https://lp.ferio.ru/parts?utm_source=otoba&amp;utm_medium=banner&amp;utm_campaign=promo&amp;erid=CQH36pWzJqVG6kaGPN5GhQ7CvB1eJr19Ueuu8wdGf7CrHP" target="_blank" rel="noopener nofollow">Найти двигатель / кпп</a>
</div> 
  
</div>
 
<div class="img-ferio"> 
<img src="https://otoba.ru/assets/reclama/company/ferio/img/bg-1.jpg" alt="Разобранный двигатель">
</div>
 
<div class="requisite">
<p style="color:#000;">Реклама. ООО "Ферио"</p>
</div>
 
</div> </div> 

<div class="clear"></div><br>
  
 </div> <!--/noindex-->
 

<div class="clear"></div> 
 				 		 
<section><div class="post-title-engine"><div class="post-title-engine_body">
<div class="title-icon"><i class="auto-rubr auto-rubr-tth"></i></div><h2 class="cont-title-dop">Технические характеристики Kia Sorento Prime 3.3 л. 6-акпп</h2>
 </div></div><div class="clear"></div>
<div class="content">
  
<div class="table-prim">
<table class="tab-prim"><caption class="tab-prim-title">Общие характеристики</caption>
<tbody><tr><td>Мощность мотора</td><td>250 л.с.</td></tr>
<tr><td>Крутящий момент</td><td>318 Нм</td></tr>
<tr><td>Разгон до 100 км/ч</td><td>8.2 с</td></tr>
<tr><td>Макс. скорость</td><td>210 км/ч</td></tr> 
<tr><td>Расход по городу</td><td>14.4 л</td></tr>
<tr><td>Расход по трассе</td><td>8.3 л</td></tr>
<tr><td>Смешанный расход</td><td>10.5 л</td></tr>
<tr><td>Объем бензобака</td><td>71 л</td></tr>
<tr><td>Снаряженная масса</td><td>1939 кг</td></tr>
<tr><td>Полная масса</td><td>2510 кг</td></tr>
<tr><td>Грузоподъемность</td><td>571 кг</td></tr>
<tr><td>Объем багажника</td><td>660 л</td></tr>
</tbody></table></div>              
 
<div class="clear"></div>
  
<div class="table-prim">
 <table class="tab-prim"><caption class="tab-prim-title">Общие размеры</caption>
<tbody><tr><td>Габаритная длина</td><td>4780 мм</td></tr>
<tr><td>Ширина</td><td>1890 мм</td></tr>
<tr><td>Высота</td><td>1690 мм</td></tr>
<tr><td>Колесная база</td><td>2780 мм</td></tr>
<tr><td>Передний свес</td><td>945 мм</td></tr>  
<tr><td>Задний свес</td><td>1055 мм</td></tr>  
<tr><td>Колея передних колес</td><td>1633 мм</td></tr>  
<tr><td>Колея задних колес</td><td>1644 мм</td></tr>
<tr><td>Клиренс</td><td>185 мм</td></tr>
<tr><td>Кол-во дверей | мест</td><td>5 | 5, 7</td></tr>
<tr><td>Размер шин</td><td>235/65 R17</td></tr>
<tr class="tab-and"><td>&nbsp;</td><td>&nbsp;</td></tr>
</tbody></table><div class="tab-dop">Другие размеры шин: 235/60 R18</div></div>    
 
<div class="clear"></div><br>
  
 <figure itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="850"><meta itemprop="height" content="650">
	<picture>
		<source srcset="img/sorento/3/tth/small/kia-sorento-prime-gabaritnye-razmery.jpg" media="(max-width: 600px)" type="image/jpeg">
		<img itemprop="contentUrl" src="img/sorento/3/tth/kia-sorento-prime-gabaritnye-razmery.jpg" loading="lazy" width="850" height="650" class="img" alt="Габаритные размеры Киа Соренто Прайм."> 
	</picture>
</figure> 
 
<div class="clear"></div> 
 
</div></section>   
<!-- TTH -->	

 <div class="clear"></div>
     	 
<!-- PROBLEMY -->
<a id="problemy"></a> 
<div class="clear"></div><br>
 
<div class="content">  

<!--// RULIVE AdCode Starts //--><div style="max-width:850px;height:450px;"><script type="text/javascript" id="generated_ID_m7x5uz8j1z">    var adScript=(function(){        var scripts = document.getElementsByTagName( 'script' );var me = scripts[ scripts.length - 1 ];var newId="generated_ID_"+(Math.random().toString(36).substr(2, 32));me.id=newId;return {'id':newId};    })();adScript.loadjscssfile=function(filename,filetype,success){if(filetype === "js"){var prms=this;var fileref=document.createElement('script');fileref.setAttribute("type", "text/javascript");fileref.setAttribute("src",filename);if(typeof(success)!=="undefined"){var done=false;fileref.onload=fileref.onreadystatechange=function(){if(!done && (!this.readyState || this.readyState === 'loaded' || this.readyState === 'complete')){done=true;success(prms);fileref.onload=fileref.onreadystatechange=null;};};}}else if(filetype === "css"){var fileref=document.createElement("link");fileref.setAttribute("rel","stylesheet");fileref.setAttribute("type", "text/css");fileref.setAttribute("href", filename);}if (typeof fileref != "undefined"){document.getElementsByTagName("head")[0].appendChild(fileref);}};var adRdFn=function(prms){mediaAd.showVideoAdBlock({'iframed':'js','deliveryUrl':'https://w.rulive.ru/show/std?scid=','siteChannelId':'223','scriptContainer':prms.id});};adScript.loadjscssfile('https://w.rulive.ru/resources/show.min.js','js',adRdFn);</script></div><!--// RULIVE AdCode Ends //-->
 
<div class="clear"></div>
 
</div> 
 
<div class="clear"></div><br> 	
<section><div class="post-title-engine"><div class="post-title-engine_body">
<div class="title-icon"><i class="auto-rubr auto-rubr-polomki"></i></div><h2 class="cont-title-dop">Достоинства, недостатки и проблемы Киа Соренто Прайм (UM)</h2>	
 </div></div><div class="clear"></div>
<div class="content">
 
<!-- КУЗОВ И САЛОН -->
<div class="polomki"> <div class="tabl-modif-title">Кузов и салон</div>
  
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">Лакокрасочное тут тонкое и сколы ржавеют быстро, но сам кузов особо не гниет</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">На форумах жалуются на недолговечное хромовое покрытие и запотевание фар</p></div>
   
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">Салон кроссовера просторный и симпатичный, оснащение всегда очень богатое</p></div>
  
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">А вот стойкость к износу слабовата, быстро теряет вид кожа на руле и сидениях</p></div>
  
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">По электрике чаще всего беспокоит штатная мультимедиа и бесключевой доступ</p></div>
  
</div>
 <!-- КУЗОВ И САЛОН -->
 
<div class="clear"></div><br>

<!-- ДВИГАТЕЛЬ -->   
 <div class="polomki"><div class="tabl-modif-title">Двигатель</div>
  
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">2.4-литровый <a href="https://otoba.ru/dvigatel/hyundai/g4kj.html" class="lk">бензиновый двигатель G4KJ</a> надежен, но есть у него слабое место</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Проблема с задирами из-за крошек катализатора все еще никак не разрешилась</p></div>
   
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">Моторы V6 объемом <a href="https://otoba.ru/dvigatel/hyundai/g6df.html" class="lk">3.3 литра G6DF</a> и <a href="https://otoba.ru/dvigatel/hyundai/g6dc.html" class="lk">3.5 литра G6DC</a> имеют огромный ресурс</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Но владельцы жалуются не только на большой расход топлива, но еще и масла</p></div>
   
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">2.2-литровый <a href="https://otoba.ru/dvigatel/hyundai/d4hb.html" class="lk">турбодизель D4HB</a> при хорошем обслуживании ходит без проблем</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Его основные проблемы связаны с топливной аппаратурой, а также клапаном егр</p></div>
  
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">После 100 тысяч км пробега необходимо проверить состояния цепи ГРМ и ТНВД</p></div>
 
 </div>
<!-- ДВИГАТЕЛЬ -->  
 
<div class="clear"></div><br>

<!-- ТРАНСМИССИЯ -->  
 <div class="polomki"><div class="tabl-modif-title">Трансмиссия</div>
    
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">6-ступенчатые <a href="https://otoba.ru/transmissii/hyundai-kia/a6mf2.html" class="lk">акпп A6MF2</a>, <a href="https://otoba.ru/transmissii/hyundai-kia/a6lf1.html" class="lk">A6LF1</a> и <a href="https://otoba.ru/transmissii/hyundai-kia/a6lf3.html" class="lk">A6LF3</a> вполне надежны и беспокоят нечасто</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">8-ступенчатую <a href="https://otoba.ru/transmissii/hyundai-kia/a8lf2.html" class="lk">акпп A8LF2</a> в первые годы выпуска регулярно меняли по гарантии</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Как и ранее массу хлопот доставляют компоненты полноприводной трансмиссии</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Во-первых, постоянного ухода требуют шлицевые соединения или они заржавеют</p></div>
  
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">А во-вторых, довольно часто встречается обрыв оси корзины фрикционов муфты</p></div>
         
</div>
 <!-- ТРАНСМИССИЯ --> 
 
<div class="clear"></div><br>

<!-- ХОДОВАЯ -->  
 <div class="polomki"><div class="tabl-modif-title">Ходовая</div>
  
<div class="polomki-plus"><p><img src="https://otoba.ru/images/content/like.jpg" class="plmn-img" alt="Значок Like">Подвеска вцелом надежная и до 100 000 км меняют только втулки стабилизатора</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Слабым местом служат задние амортизаторы, нередко они ходят менее 50 000 км</p></div>
 
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Тормозные диски тут маловаты и при агрессивной езде быстро появляется биение</p></div>
  
<div class="polomki-minus"><p><img src="https://otoba.ru/images/content/unlike.jpg" class="plmn-img" alt="Значок not Like">Рулевая рейка часто начинала шуметь на малом пробеге и ее меняли по гарантии</p></div>
  
</div>
 <!-- ХОДОВАЯ --> 
 
<div class="clear"></div> 

</div></section>
<!-- PROBLEMY -->
 
<div class="clear"></div>
 
<!-- CENA -->
<a id="cena"></a>	
<div class="clear"></div>
 
<!--noindex--><div class="content">   
<div class="block-reclama"><div class="banner-ma">
 
<div class="slogan-ma">
<p class="zagl">Контрактные двигатели и коробки передач</p>
<div class="slogan-ma-osn">
<div class="logo-ma"><div class="slogan-logo-ma"><img src="https://otoba.ru/assets/reclama/company/ma/img/logo.png" loading="lazy" width="390" height="100" alt="Логотип МоторАкпп"></div>

<div class="text-ma"> 
<p>• Моторы, коробки и другие запчасти из Японии, Европы, ОАЭ, США</p>
<p>• Без посредников и дополнительных наценок</p>
<p>• В наличии на складе и под заказ</p>
</div> 

<div class="button-ma"><a href="https://motorakpp.ru" target="_blank" rel="noopener nofollow">Перейти в каталог</a></div> 
</div> 
 
</div></div>
   
<div class="clear"></div>
  
<div class="spravka-ma">
<p style="color:#fff;opacity:.6;">РЕКЛАМА: ИП Овчинников А.А. ИНН 772643633896</p>
</div>
 
<div class="img-ma"> 
 
<picture>
<source media="(max-width: 700px)" srcset="https://otoba.ru/assets/reclama/company/ma/img/bg-ma-small.jpg">
<source media="(min-width: 701px)" srcset="https://otoba.ru/assets/reclama/company/ma/img/bg-ma.jpg">
<img src="https://otoba.ru/assets/reclama/company/ma/img/bg-ma.jpg" alt="Баннер МоторАкпп">
</picture>
 
</div>

</div></div> </div>   
 <!--/noindex-->
 
<div class="clear"></div><br>
  
<section><div class="post-title-engine"><div class="post-title-engine_body">
<div class="title-icon"><i class="auto-rubr auto-rubr-cena"></i></div><h2 class="cont-title-dop">Цена Kia Sorento Prime (UM) на вторичном рынке</h2>
 </div></div><div class="clear"></div>
<div class="content">

<p>У нас на вторичке предлагают более двух сотен кроссоверов стоимостью от 1 500 000 рублей.</p>

 <div class="clear"></div>
 
 <!--AUTO CARD-->
<div class="card-auto"><div class="card-auto_title">Kia Sorento Prime</div>
<div class="card-auto_cena">1 600 000 ₽</div>
<div class="card-auto_body">
<div class="card-auto_text">

<table class="card-auto_table">
<tbody><tr><td>Год выпуска:</td><td><b>2016</b></td></tr>
<tr><td>Пробег:</td><td><b>110 000 км</b></td></tr>
<tr><td>Кузов:</td><td>Внедорожник 5 дв.</td></tr>
<tr><td>Цвет:</td><td>Белый</td></tr>
<tr><td>Двигатель:</td><td>3.3 л / 250 л.с. / Бензин</td></tr>
<tr><td>Коробка:</td><td>Автоматическая</td></tr>
<tr><td>Привод:</td><td>Полный</td></tr>
<tr><td>Состояние:</td><td>Не требует ремонта</td></tr>
</tbody></table></div>

<div class="card-auto_foto">
<figure itemscope="" itemtype="https://schema.org/ImageObject">
	<meta itemprop="width" content="600"><meta itemprop="height" content="350">
<picture>
<img itemprop="contentUrl" src="img/sorento/3/ceny/bu-kia-sorento-prime-2016.jpg" loading="lazy" width="600" height="350" alt="Подержанный Kia Sorento Prime (UM)">  
</picture></figure>  
</div>

</div> <div class="tab-dop"><p>* Цена на данное авто указана справочно</p></div></div> 
 <!--AUTO CARD-->	
 
<div class="clear"></div> 
 
</div></section>
<!-- CENA -->

 <div class="clear"></div>
 
<!-- DOP-MAT -->
 <div class="clear"></div> 
  
<div class="content"><div class="recl" style="margin: 1em auto;text-align: center; display: block; clear: both;">
 
<!-- Yandex.RTB R-A-1578237-7 -->
<div id="yandex_rtb_R-A-1578237-7"></div>
<script>
window.yaContextCb.push(() => {
    Ya.Context.AdvManager.render({
        "blockId": "R-A-1578237-7",
        "renderTo": "yandex_rtb_R-A-1578237-7"
    })
})
</script>
  
</div></div> 
 
<div class="clear"></div> <br> 
 <div class="post-title-engine"><div class="post-title-engine_body">
<div class="title-icon"><i class="auto-rubr auto-rubr-info"></i></div> <div class="dop-mat-title">Дополнительные материалы</div>
 </div></div><div class="clear"></div>
<div class="content">
 
<div class="vid-object">
<p class="description">Обзор Киа Соренто Прайм пробегом от Авто Плюс</p>	
<div class="vid"> 
<img src="https://img.youtube.com/vi/ZBTh7N8yxNY/hqdefault.jpg" loading="lazy" width="850" height="450" alt="Премиум по бюджетной цене. Реально ли содержать Kia Sorento Prime? | Подержанные автомобили">
<iframe width="850" height="450" src="https://www.youtube.com/embed/ZBTh7N8yxNY" srcdoc="&lt;style&gt;*{padding:0;margin:0;overflow:hidden} img,span{position:absolute;width:100%;top:0;bottom:0;margin:auto} span{height:1.5em;text-align:center;font:6em/1.5 sans-serif;color:white;text-shadow:0 0 .5em #000; }&lt;/style&gt;
  &lt;a href=https://www.youtube.com/embed/ZBTh7N8yxNY?autoplay=1&gt;
  &lt;img src=https://img.youtube.com/vi/ZBTh7N8yxNY/hqdefault.jpg  loading='lazy' alt='Премиум по бюджетной цене. Реально ли содержать Kia Sorento Prime? | Подержанные автомобили'&gt;&lt;span&gt;►&lt;/span&gt;&lt;/a&gt;" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" title="Премиум по бюджетной цене. Реально ли содержать Kia Sorento Prime? | Подержанные автомобили"></iframe>
</div></div>
 
</div> 
<!-- DOP-MAT -->

<div class="clear"></div><!-- <div class="content" style="margin:0 0 1em">
<p><meta itemprop="author" content="Андрей Малыхин">Автор статьи:  <a href="https://otoba.ru/info/politika-konfidencialnosti.html#author" target="_blank">Андрей Малыхин</a></p>
</div>  --> 

<aside class="content-others" itemscope="" itemtype="https://schema.org/WPSideBar">
<div class="content-others-info"><!-- <p class="others-info-title">Читать еще:</p> -->
	
<div class="clear"></div><br>
  <div class="clear"></div><div class="rekomend-content"><div class="content-reklama">
 
 <!-- Yandex.RTB R-A-1578237-29 -->
<div id="yandex_rtb_R-A-1578237-29"></div>
<script>
window.yaContextCb.push(() => {
    Ya.Context.AdvManager.render({
        "blockId": "R-A-1578237-29",
        "renderTo": "yandex_rtb_R-A-1578237-29",
        "type": "feed"
    })
})
</script>
  
</div></div><div class="clear"></div> 
<div class="clear"></div></div></aside>

</article>
```

Ожидаемый ответ:
```json
[
    {
        generation: {
            brand: "KIA",
            series: "Sorento",
            name: "3",
            is_restyling: false,
            start_year: 2014,
            end_year: 2017
        },
        trims: [
            {
                name: "",
                engine: "G4KJ",
                transmission: "A6MF2",
                body: "UM",
                drive_type: "full",
            },
            {
                name: "",
                engine: "G6DF",
                transmission: "A6LF1",
                body: "UM",
                drive_type: "full"
            },
            {
                name: "",
                engine: "D4HB",
                transmission: "A6LF3",
                body: "UM",
                drive_type: "full"
            }
        ]
    },
    {
        generation: {
            brand: "KIA",
            series: "Sorento",
            name: "3",
            is_restyling: true,
            start_year: 2017,
            end_year: 2020
        },
        trims: [
            {
                name: "",
                engine: "G4KJ",
                transmission: "A6MF2",
                body: "UM",
                drive_type: "front"
            },
            {
                name: "",
                engine: "G6DC",
                transmission: "A8LF1,
                body: "UM",
                drive_type: "full"
            },
            {
                name: "",
                engine: "D4HB",
                transmission: "A8LF2,
                body: "UM",
                drive_type: "full"
            }
        ]
    }
]
```

HTML:\n
    """ + html + '\nОтвет:\n'
