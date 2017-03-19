var gauge = c3.generate({
    bindto: d3.select('#gauge'),
    data: {
        url: '/powermon/api/last-day-usage',
        type: 'gauge'
    },
    gauge: {
      min: 0, // 0 is default, //can handle negative min e.g. vacuum / voltage / current flow / rate of change
      max: 35, // 100 is default
      units: ' KWh',
      width: 100, // for adjusting arc thickness
      expand: true,
      label: {
          format: function (value, ratio) {
            return value;
	  }
      }
    },
    color: {
        pattern: ['#60B044', '#F6C600','#F97600','#FF0000'], // the three color levels for the percentage values.
        threshold: {
            unit: 'KWh', // percentage is default
            max: 35, // 100 is default
            values: [20, 25, 30]
        }
    },
    size: {
        height: 180
    }
    });

var chart = c3.generate({
  data: {
    url: '/powermon/api/home-report',
    x: 'sample_time',
    xFormat: '%Y-%m-%d %H:%M:%S'
  },
  axis: {
    x: {
      type: 'timeseries',
      tick: {
        format: '%H:%M:%S'
      }
    }
  }
});

