const fetchQueryResult = async (query: string) => {
    try {
        const response = await fetch('http://localhost:5000/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        const data = await response.json();
        console.log(data);
        if (data["error"]){
            return 'Lo siento no tengo respuesta'
        }
        return data
    } catch (error) {
        console.error('Error fetching data:', error);
        return 'Lo siento no tengo respuesta'
    }
};

export { fetchQueryResult };