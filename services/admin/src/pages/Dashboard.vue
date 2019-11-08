<template>
  <div>

    <!--Stats cards-->
    <div class="row">
      <div class="col-md-6 col-xl-2" v-for="stats in statsCards" :key="stats.title">
        <stats-card>
          <div class="icon-big text-center" :class="`icon-${stats.type}`" slot="header">
            <i :class="stats.icon"></i>
          </div>
          <div class="numbers" slot="content">
            <p>{{stats.title}}</p>
            {{stats.value}}
          </div>
          <div class="stats" slot="footer">
            <i :class="stats.footerIcon"></i> {{stats.footerText}}
          </div>
        </stats-card>
      </div>
    </div>

    <!--Charts-->
    <div class="row">

      <div class="col-md-6" v-if="usersChart.data.series.length > 0">
        <chart-card title="Users behavior"
                    sub-title="Distribution by media type per day"
                    :chart-data="usersChart.data"
                    :chart-options="usersChart.options">
          <span slot="footer">
            <i class="ti-reload"></i> Updated now
          </span>
          <div slot="legend" v-for="(legend, index) in usersChart.data.legends">
            <i class="fa fa-circle" :class="`text-${usersChart.data.colors[index]}`"></i> {{legend}}
          </div>
        </chart-card>
      </div>

      <div class="col-md-6" v-if="depositsPieChart.data.series.length > 0">
        <chart-card title="Deposits"
                    sub-title="Distribution by Media Type"
                    :chart-data="depositsPieChart.data"
                    chart-type="Pie">
          <span slot="footer" >
            <i class="ti-timer"></i> Updated now</span>
          <div slot="legend" v-for="(label, index) in depositsPieChart.data.labels" :key="label">
            <i class="fa fa-circle" :class="`text-${depositsPieChart.data.colors[index]}`"></i> {{label}}
          </div>
        </chart-card>
      </div>

      <!-- <div class="col-md-6 col-12">
        <chart-card title="2015 Sales"
                    sub-title="All products including Taxes"
                    :chart-data="activityChart.data"
                    :chart-options="activityChart.options">
          <span slot="footer">
            <i class="ti-check"></i> Data information certified
          </span>
          <div slot="legend">
            <i class="fa fa-circle text-info"></i> Tesla Model S
            <i class="fa fa-circle text-warning"></i> BMW 5 Series
          </div>
        </chart-card>
      </div> -->

    </div>

  </div>
</template>
<script>
import { StatsCard, ChartCard } from "@/components/index";
import Chartist from 'chartist';
import axios from 'axios';

export default {
  components: {
    StatsCard,
    ChartCard
  },
  methods: {
    convertSize(value) {
      if (value <= 1.0e+6) {
        return Math.round((value/1.0e+3)).toString() + 'KB'
      }
      if (value > 1.0e+6 && value <= 1.0e+9) {
        return Math.round((value/1.0e+6)).toString() + 'MB'
      }
      if (value > 1.0e+9) {
        return Math.round((value/1.0e+9)).toString() + 'GB'
      }
    },
    fetchCountByMediaTypes(list_of_deposits) {
      var media_types = new Map()
      for(var i=0; i<list_of_deposits.length; i++) {
        var mt = list_of_deposits[i]['deposit_metadata']['media_type']
        if(media_types.has(mt)){
          media_types.set(mt, media_types.get(mt)+1)
        } else {
          media_types.set(mt,1)
        }
      }
      var keys = [];
      var values = [];
      for(const [key, value] of media_types.entries()) {
        keys.push(key);
        values.push(value);
      }
      return [keys, values]
    },
    fetchCountByMediaTypesGroupByDay(list_of_deposits) {
      var count_by_date = new Map();
      var legends = [];
      for (var i = 0; i < list_of_deposits.length; i++) {
        var mt = list_of_deposits[i]['deposit_metadata']['media_type']
        var cd = list_of_deposits[i]['deposit_metadata']['create_date']
        if(!legends.includes(mt)) {
          legends.push(mt);
        }
        if (count_by_date.has(cd)) {
          var media_types = count_by_date.get(cd)
          if(media_types.has(mt)) {
            media_types.set(mt, media_types.get(mt)+1)
          } else {
            media_types.set(mt, 1)
          }

          count_by_date.set(cd, media_types)
        } else {
          var media_types = new Map()
          media_types.set(mt, 1)
          count_by_date.set(cd, media_types);
        }
      }
      var keys = [];
      var values = [];
      count_by_date = new Map([...count_by_date.entries()].sort());
      for(const [key, value] of count_by_date.entries()) {
        keys.push(key);
        for(var i=0; i<legends.length; i++) {
          var value_to_be_pushed = 0;
          if(value.has(legends[i])) {
            value_to_be_pushed = value.get(legends[i]);
          }
          if(i>=values.length) {
            values.push([value_to_be_pushed])
          }
          else {
            values[i].push(value_to_be_pushed)
          }
        }


        // for(const [key2, value2] of media_types.entries()) {
        //   var index = legends.indexOf(key2)
        //   if(index>=values.length) {
        //     values.push([value2])
        //   }
        //   else {
        //     values[index].push(value2)
        //   }
        // }
      }
      console.log(keys, values, legends)
      return [keys, values, legends]
    }

  },
  /**
   * Chart data used to render stats, charts. Should be replaced with server data
   */
  data() {
    return {
       statsCards: [
        {
          type: "warning",
          icon: "ti-server",
          title: "Used Size",
          value: '',
          footerText: "Updated now",
          footerIcon: "ti-reload"
        },
        {
          type: "success",
          icon: "ti-wallet",
          title: "Deposits",
          value: '',
          footerText: "Updated now",
          footerIcon: "ti-reload"
        },
        {
          type: "danger",
          icon: "ti-pulse",
          title: "Largest File",
          value: '',
          footerText: "Updated now",
          footerIcon: "ti-reload"
        }
        // {
        //   type: "info",
        //   icon: "ti-twitter-alt",
        //   title: "Followers",
        //   value: "+45",
        //   footerText: "Updated now",
        //   footerIcon: "ti-reload"
        // }
      ],
      usersChart: {
        data: {
          labels: [],
          series: [],
          colors: []
        },
        options: {
          low: 0,
          high: 10,
          showArea: true,
          height: "245px",
          axisX: {
            showGrid: false
          },
          lineSmooth: Chartist.Interpolation.simple({
            divisor: 3
          }),
          showLine: true,
          showPoint: false,
          scaleMinSpace: 1,
          onlyInteger: true
        }
      },
      activityChart: {
        data: {
          labels: [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec"
          ],
          series: [
            [542, 543, 520, 680, 653, 753, 326, 434, 568, 610, 756, 895],
            [230, 293, 380, 480, 503, 553, 600, 664, 698, 710, 736, 795]
          ]
        },
        options: {
          seriesBarDistance: 10,
          axisX: {
            showGrid: false
          },
          height: "245px"
        }
      },
      depositsPieChart: {
        data: {
          labels: [],
          series: [],
          colors: []
        },
        options: {}
      },
      mongo_data: {}
    };
  },
  mounted() {
    axios.get('../api/store/buckets', {params: {'bucket_name': '3deposit'}})
    .then(response => {
      this.statsCards[0].value = this.convertSize(response.data.bucket_size);
      this.statsCards[1].value = response.data.num_files;
      this.statsCards[2].value = this.convertSize(response.data.largest_file);
    });
    axios.get('../api/mongo')
    .then(response => {
      this.mongo_data = response.data.stats
      var result_list = this.fetchCountByMediaTypes(this.mongo_data)
      this.depositsPieChart.data.labels = result_list[0]
      this.depositsPieChart.data.series = result_list[1]
      this.depositsPieChart.data.colors = ['info', 'warning', 'danger']

      var result_list_2 = this.fetchCountByMediaTypesGroupByDay(this.mongo_data)

      this.usersChart.data.labels = result_list_2[0]
      this.usersChart.data.series = result_list_2[1]
      this.usersChart.data.legends = result_list_2[2]
      this.usersChart.data.colors = ['info', 'warning', 'danger']
    });
  }
};
</script>
<style>
</style>
