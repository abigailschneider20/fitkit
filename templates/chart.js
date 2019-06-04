class Chart extends React.Component {
    constructor(props) {

    }

    componentWillReceiveProps(nextProps){
    if (nextProps.chartType !== this.state.chartType) {
    this.setState({chartType: nextProps.chartType})
    }
  }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            chartData : {},
            chartType: 'Line',
            isLoaded: false
        };
        this.handleVisualChange = this.handleVisualChange.bind(this);
    }
    componentDidMount(){
        this.getChartData();
    }
    handleVisualChange(value){
        console.log('testing value in App.js', value);
        this.setState({chartType: value});
    }
    getChartData(){
        $.ajax({'/chart', function(data) {
            console.log('original data:', data);
            const arrCat = [];
            const arrTotal = [];
            for (let i = 0, len = data.length; i<len; i++){
                arrCat.push(data[i].Cat);
                arrTotal.push(data[i].Total);
            }
            console.log('just cats:', arrCat);
            console.log('just total:', arrTotal);
            this.setState({
                chartData:{
                    labels: arrCat,
                    datasets:[
                    {
                        label: 'IDK Transactions',
                        data: arrTotal,
                        background Color: 'rgba(255, 206, 86, 2)'
                    }
                  ]
                }
            },
            isLoaded: true
        });
        }.bind(this),
        });
    }

render(){
    let chartToBeDisplayed = null;
    switch(this.state.chartType) {
        case 'Line':
        chartToBeDisplayed = <LineChart chartData={this.state.chartData} />;
        break;
    default:
    console.log('Something went wrong...');
    }
    return(
        <div className = 'App'> 
        <Header />
        <Dropdown onVisualChange = {this.handleVisualChange} />
        <div className = "ChartArea">
        {this.state.isLoaded ? {chartToBeDisplayed}:<div>Loading...</div>}
        </div>
        </div>
        );
    }
}

export default App;