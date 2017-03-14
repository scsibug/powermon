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
