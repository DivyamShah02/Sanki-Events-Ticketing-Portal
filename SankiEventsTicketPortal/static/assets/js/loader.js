function toggle_loader() {
    try{
        document.getElementById('offcanvasNavbar').classList.toggle('none-div');
    }
    catch(error){
        console.log(error);
    }
    document.getElementById('main-content').classList.toggle('blur');
    document.getElementById('spinner').classList.toggle('none-div');
    document.getElementById('spinner').classList.toggle('spinner-container');
}
