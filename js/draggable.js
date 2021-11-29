const empty = document.querySelector("right_div");
const controller = document.querySelector("controller");
var name;

document.addEventListener('dragstart',(e)=>{
    name = e.target;
},false);

document.addEventListener('drag',(e)=>{
    e.target.style.border = '5px dashed red';
    empty.style.border = '5px dashed red';
},false);

document.addEventListener('dragend',(e)=>{
    e.target.style.border = 'none';
    empty.style.border = 'none';
    controller.innerHTML = "画图";
    controller.style.color = 'black';
},false);

empty.addEventListener('dragenter',(e)=>{
    controller.innerHTML= name;
    controller.style.color = 'red';
},false);

empty.addEventListener('dropenter',(e)=>{
    e.preventDefault();
},false);

empty.addEventListener('dropover',(e)=>{
    e.preventDefault();
},false);

empty.addEventListener('drop',(e)=>{
    e.preventDefault();
    e.target.appendChild(document.querySelector('img[alt=${name}]'));
},false);