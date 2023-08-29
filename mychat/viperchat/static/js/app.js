(async function(){
    try{
        const weatherDiv = document.getElementById('weather')
        console.log(weatherDiv.children)
        const weather_key = '2f102f69deb149b182c134020230608';
        const response = await fetch(`http://api.weatherapi.com/v1/forecast.json?key=${weather_key}&q=auto:ip`);
        const data = await response.json();
        const {location, current} = data;
        const weather = weatherDiv.appendChild(document.createElement('span'));
        const celsiusSymbol = '°'
        weather.innerText = `Location: ${location.name} | temp: ${current.temp_c} ${celsiusSymbol}C`;
        console.log(data);
    }catch(error) {
        console.log(error);
    }
}());