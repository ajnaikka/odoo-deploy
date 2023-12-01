odoo.define('uaa_dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');
    var view_registry = require('web.view_registry');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');

    var _t = core._t;
    var _lt = core._lt;

    var UAADashboardView = AbstractAction.extend({
        cssLibs: [
            '/sr_uaa_dashboard/static/src/css/lib/nv.d3.css'
        ],
        jsLibs: [
            '/sr_uaa_dashboard/static/src/js/lib/d3.min.js'
        ],
        events: {
            'click .my_customers': 'action_my_customers',
            'click .my_new_enquires': 'action_my_new_enquires',
            //        'click .my_upcoming_enquires': 'action_my_upcoming_enquires',
            'click .my_upcoming_services': 'action_my_upcoming_services',
            'click .my_open_enquires': 'action_my_open_enquires',
            'click .my_close_enquires': 'action_my_close_enquires',
            'click .my_cancelled_enquires': 'action_my_cancelled_enquires',
            'click .my_paid_enquires': 'action_my_paid_enquires',
            'click .my_enquires': 'action_my_enquires',
            'click .my_airports': 'action_my_airports',
        },
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = [
                "UAADashboardTemplate"
            ];
            var dashboard_data = [];
            var self = this;
            if (context.tag == 'uaa_dashboard') {
                self._rpc({
                    model: 'uaa.dashboard',
                    method: 'get_info',
                }, []).then(function (result) {
                    self.dashboard_data = result[0]
                    self.render();
                    self.href = window.location.href;
                });
            }
        },
        willStart: function () {
            return $.when(ajax.loadLibs(this), this._super());
        },
        start: function () {
            var self = this;
            return this._super().then(function () {
                self.render_graphs();
            });
        },

        render_graphs: function () {
            var self = this;
            self.render_enquiry_weekly_graph();
            self.render_enquiry_graph();
            self.render_airport_graph();
            self.render_country_graph();
        },
        render: function () {
            var super_render = this._super;
            var self = this;
            var uaa_dashboard_qweb = QWeb.render('UAADashboardTemplate', {
                widget: self,
            });
            $(".o_control_panel").addClass("o_hidden");
            $(uaa_dashboard_qweb).prependTo(self.$el);
            return uaa_dashboard_qweb
        },
        reload: function () {
            window.location.href = this.href;

        },

        render_country_graph: function () {
            var self = this;
            //        var color = d3.scale.category10();
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
                '#ffa433', '#ffc25b', '#f8e54b'];
            var color = d3.scale.ordinal().range(colors);
            rpc.query({
                model: "airport.enquiry",
                method: "get_the_country_details",
            }).then(function (data) {
                var fData = data[0];
                var dept = data[1];
                var id = self.$('.country_graph')[0];
                var barColor = '#ff618a';
                fData.forEach(function (d) {
                    var total = 0;
                    for (var dpt in dept) {
                        total += d.enquiry[dept[dpt]];
                    }
                    d.total = total;
                });

                // function to handle histogram.
                function histoGram(fD) {
                    var hG = {}, hGDim = { t: 60, r: 0, b: 30, l: 0 };
                    hGDim.w = 350 - hGDim.l - hGDim.r,
                        hGDim.h = 200 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                        .domain(fD.map(function (d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                        .domain([0, d3.max(fD, function (d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                        .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function (d) { return x(d[0]); })
                        .attr("y", function (d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function (d) { return hGDim.h - y(d[1]); })
                        .attr('fill', barColor)
                        .on("mouseover", mouseover)// mouseover is defined below.
                        .on("mouseout", mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function (d) { return d3.format(",")(d[1]) })
                        .attr("x", function (d) { return x(d[0]) + x.rangeBand() / 2; })
                        .attr("y", function (d) { return y(d[1]) - 5; })
                        .attr("text-anchor", "middle");

                    function mouseover(d) {  // utility function to be called on mouseover.
                        // filter for selected state.
                        var st = fData.filter(function (s) { return s.l_month == d[0]; })[0],
                            nD = d3.keys(st.enquiry).map(function (s) { return { type: s, enquiry: st.enquiry[s] }; });

                        // call update functions of pie-chart and legend.
                        pC.update(nD);
                        leg.update(nD);
                    }

                    function mouseout(d) {    // utility function to be called on mouseout.
                        // reset the pie-chart and legend.
                        pC.update(tF);
                        leg.update(tF);
                    }

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function (nD, color) {
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function (d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function (d) { return y(d[1]); })
                            .attr("height", function (d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function (d) { return d3.format(",")(d[1]) })
                            .attr("y", function (d) { return y(d[1]) - 5; });
                    }
                    return hG;
                }

                // function to handle pieChart.
                function pieChart(pD) {
                    var pC = {}, pieDim = { w: 250, h: 250 };
                    pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

                    // create svg for pie chart.
                    var piesvg = d3.select(id).append("svg")
                        .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
                        .attr("transform", "translate(" + pieDim.w / 2 + "," + pieDim.h / 2 + ")");

                    // create function to draw the arcs of the pie slices.
                    var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

                    // create a function to compute the pie slice angles.
                    var pie = d3.layout.pie().sort(null).value(function (d) { return d.enquiry; });

                    // Draw the pie slices.
                    piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
                        .each(function (d) { this._current = d; })
                        .attr("fill", function (d, i) { return color(i); })
                        .on("mouseover", mouseover).on("mouseout", mouseout);

                    // create function to update pie-chart. This will be used by histogram.
                    pC.update = function (nD) {
                        piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                            .attrTween("d", arcTween);
                    }
                    // Utility function to be called on mouseover a pie slice.
                    function mouseover(d, i) {
                        // call the update function of histogram with new data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.enquiry[d.data.type]];
                        }), color(i));
                    }
                    //Utility function to be called on mouseout a pie slice.
                    function mouseout(d) {
                        // call the update function of histogram with all data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.total];
                        }), barColor);

                    }
                    // Animating the pie-slice requiring a custom function which specifies
                    // how the intermediate paths should be drawn.
                    function arcTween(a) {
                        var i = d3.interpolate(this._current, a);
                        this._current = i(0);
                        return function (t) { return arc(i(t)); };
                    }
                    return pC;
                }

                // function to handle legend.
                function legend(lD) {
                    var leg = {};

                    // create table for legend.
                    var legend = d3.select(id).append("table").attr('class', 'legend');

                    // create one row per segment.
                    var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");

                    // create the first column for each segment.
                    tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                        .attr("width", '16').attr("height", '16')
                        .attr("fill", function (d, i) { return color(i); })

                    // create the second column for each segment.
                    tr.append("td").text(function (d) { return d.type; });

                    // create the third column for each segment.
                    tr.append("td").attr("class", 'legendFreq')
                        .text(function (d) { return d.l_month; });

                    // create the fourth column for each segment.
                    tr.append("td").attr("class", 'legendPerc')
                        .text(function (d) { return getLegend(d, lD); });

                    // Utility function to be used to update the legend.
                    leg.update = function (nD) {
                        // update the data attached to the row elements.
                        var l = legend.select("tbody").selectAll("tr").data(nD);

                        // update the frequencies.
                        l.select(".legendFreq").text(function (d) { return d3.format(",")(d.enquiry); });

                        // update the percentage column.
                        l.select(".legendPerc").text(function (d) { return getLegend(d, nD); });
                    }

                    function getLegend(d, aD) { // Utility function to compute percentage.
                        var perc = (d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        if (isNaN(perc)) {
                            return d3.format("%")(0);
                        }
                        else {
                            return d3.format("%")(d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        }
                    }

                    return leg;
                }
                // calculate total frequency by segment for all state.
                var tF = dept.map(function (d) {
                    return { type: d, enquiry: d3.sum(fData.map(function (t) { return t.enquiry[d]; })) };
                });

                // calculate total frequency by state for all segment.
                var sF = fData.map(function (d) { return [d.l_month, d.total]; });

                var hG = histoGram(sF), // create the histogram.
                    pC = pieChart(tF), // create the pie-chart.
                    leg = legend(tF);  // create the legend.
            });
        },
        render_airport_graph: function () {
            var self = this;
            //        var color = d3.scale.category10();
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
                '#ffa433', '#ffc25b', '#f8e54b'];
            var color = d3.scale.ordinal().range(colors);
            rpc.query({
                model: "airport.enquiry",
                method: "get_the_airport_details",
            }).then(function (data) {
                var fData = data[0];
                var dept = data[1];
                var id = self.$('.airport_graph')[0];
                var barColor = '#ff618a';
                fData.forEach(function (d) {
                    var total = 0;
                    for (var dpt in dept) {
                        total += d.enquiry[dept[dpt]];
                    }
                    d.total = total;
                });

                // function to handle histogram.
                function histoGram(fD) {
                    var hG = {}, hGDim = { t: 60, r: 0, b: 30, l: 0 };
                    hGDim.w = 350 - hGDim.l - hGDim.r,
                        hGDim.h = 200 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                        .domain(fD.map(function (d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                        .domain([0, d3.max(fD, function (d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                        .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function (d) { return x(d[0]); })
                        .attr("y", function (d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function (d) { return hGDim.h - y(d[1]); })
                        .attr('fill', barColor)
                        .on("mouseover", mouseover)// mouseover is defined below.
                        .on("mouseout", mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function (d) { return d3.format(",")(d[1]) })
                        .attr("x", function (d) { return x(d[0]) + x.rangeBand() / 2; })
                        .attr("y", function (d) { return y(d[1]) - 5; })
                        .attr("text-anchor", "middle");

                    function mouseover(d) {  // utility function to be called on mouseover.
                        // filter for selected state.
                        var st = fData.filter(function (s) { return s.l_month == d[0]; })[0],
                            nD = d3.keys(st.enquiry).map(function (s) { return { type: s, enquiry: st.enquiry[s] }; });

                        // call update functions of pie-chart and legend.
                        pC.update(nD);
                        leg.update(nD);
                    }

                    function mouseout(d) {    // utility function to be called on mouseout.
                        // reset the pie-chart and legend.
                        pC.update(tF);
                        leg.update(tF);
                    }

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function (nD, color) {
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function (d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function (d) { return y(d[1]); })
                            .attr("height", function (d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function (d) { return d3.format(",")(d[1]) })
                            .attr("y", function (d) { return y(d[1]) - 5; });
                    }
                    return hG;
                }

                // function to handle pieChart.
                function pieChart(pD) {
                    var pC = {}, pieDim = { w: 250, h: 250 };
                    pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

                    // create svg for pie chart.
                    var piesvg = d3.select(id).append("svg")
                        .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
                        .attr("transform", "translate(" + pieDim.w / 2 + "," + pieDim.h / 2 + ")");

                    // create function to draw the arcs of the pie slices.
                    var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

                    // create a function to compute the pie slice angles.
                    var pie = d3.layout.pie().sort(null).value(function (d) { return d.enquiry; });

                    // Draw the pie slices.
                    piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
                        .each(function (d) { this._current = d; })
                        .attr("fill", function (d, i) { return color(i); })
                        .on("mouseover", mouseover).on("mouseout", mouseout);

                    // create function to update pie-chart. This will be used by histogram.
                    pC.update = function (nD) {
                        piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                            .attrTween("d", arcTween);
                    }
                    // Utility function to be called on mouseover a pie slice.
                    function mouseover(d, i) {
                        // call the update function of histogram with new data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.enquiry[d.data.type]];
                        }), color(i));
                    }
                    //Utility function to be called on mouseout a pie slice.
                    function mouseout(d) {
                        // call the update function of histogram with all data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.total];
                        }), barColor);

                    }
                    // Animating the pie-slice requiring a custom function which specifies
                    // how the intermediate paths should be drawn.
                    function arcTween(a) {
                        var i = d3.interpolate(this._current, a);
                        this._current = i(0);
                        return function (t) { return arc(i(t)); };
                    }
                    return pC;
                }

                // function to handle legend.
                function legend(lD) {
                    var leg = {};

                    // create table for legend.
                    var legend = d3.select(id).append("table").attr('class', 'legend');

                    // create one row per segment.
                    var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");

                    // create the first column for each segment.
                    tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                        .attr("width", '16').attr("height", '16')
                        .attr("fill", function (d, i) { return color(i); })

                    // create the second column for each segment.
                    tr.append("td").text(function (d) { return d.type; });

                    // create the third column for each segment.
                    tr.append("td").attr("class", 'legendFreq')
                        .text(function (d) { return d.l_month; });

                    // create the fourth column for each segment.
                    tr.append("td").attr("class", 'legendPerc')
                        .text(function (d) { return getLegend(d, lD); });

                    // Utility function to be used to update the legend.
                    leg.update = function (nD) {
                        // update the data attached to the row elements.
                        var l = legend.select("tbody").selectAll("tr").data(nD);

                        // update the frequencies.
                        l.select(".legendFreq").text(function (d) { return d3.format(",")(d.enquiry); });

                        // update the percentage column.
                        l.select(".legendPerc").text(function (d) { return getLegend(d, nD); });
                    }

                    function getLegend(d, aD) { // Utility function to compute percentage.
                        var perc = (d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        if (isNaN(perc)) {
                            return d3.format("%")(0);
                        }
                        else {
                            return d3.format("%")(d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        }
                    }

                    return leg;
                }
                // calculate total frequency by segment for all state.
                var tF = dept.map(function (d) {
                    return { type: d, enquiry: d3.sum(fData.map(function (t) { return t.enquiry[d]; })) };
                });

                // calculate total frequency by state for all segment.
                var sF = fData.map(function (d) { return [d.l_month, d.total]; });

                var hG = histoGram(sF), // create the histogram.
                    pC = pieChart(tF), // create the pie-chart.
                    leg = legend(tF);  // create the legend.
            });
        },
        render_enquiry_graph: function () {
            var self = this;
            //        var color = d3.scale.category10();
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
                '#ffa433', '#ffc25b', '#f8e54b'];
            var color = d3.scale.ordinal().range(colors);
            rpc.query({
                model: "airport.enquiry",
                method: "get_the_monthly_enquiry",
            }).then(function (data) {
                var fData = data[0];
                var dept = data[1];
                var id = self.$('.enquiry_graph')[0];
                var barColor = '#ff618a';
                fData.forEach(function (d) {
                    var total = 0;
                    for (var dpt in dept) {
                        total += d.enquiry[dept[dpt]];
                    }
                    d.total = total;
                });

                // function to handle histogram.
                function histoGram(fD) {
                    var hG = {}, hGDim = { t: 60, r: 0, b: 30, l: 0 };
                    hGDim.w = 350 - hGDim.l - hGDim.r,
                        hGDim.h = 200 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                        .domain(fD.map(function (d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                        .domain([0, d3.max(fD, function (d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                        .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function (d) { return x(d[0]); })
                        .attr("y", function (d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function (d) { return hGDim.h - y(d[1]); })
                        .attr('fill', barColor)
                        .on("mouseover", mouseover)// mouseover is defined below.
                        .on("mouseout", mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function (d) { return d3.format(",")(d[1]) })
                        .attr("x", function (d) { return x(d[0]) + x.rangeBand() / 2; })
                        .attr("y", function (d) { return y(d[1]) - 5; })
                        .attr("text-anchor", "middle");

                    function mouseover(d) {  // utility function to be called on mouseover.
                        // filter for selected state.
                        var st = fData.filter(function (s) { return s.l_month == d[0]; })[0],
                            nD = d3.keys(st.enquiry).map(function (s) { return { type: s, enquiry: st.enquiry[s] }; });

                        // call update functions of pie-chart and legend.
                        pC.update(nD);
                        leg.update(nD);
                    }

                    function mouseout(d) {    // utility function to be called on mouseout.
                        // reset the pie-chart and legend.
                        pC.update(tF);
                        leg.update(tF);
                    }

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function (nD, color) {
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function (d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function (d) { return y(d[1]); })
                            .attr("height", function (d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function (d) { return d3.format(",")(d[1]) })
                            .attr("y", function (d) { return y(d[1]) - 5; });
                    }
                    return hG;
                }

                // function to handle pieChart.
                function pieChart(pD) {
                    var pC = {}, pieDim = { w: 250, h: 250 };
                    pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

                    // create svg for pie chart.
                    var piesvg = d3.select(id).append("svg")
                        .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
                        .attr("transform", "translate(" + pieDim.w / 2 + "," + pieDim.h / 2 + ")");

                    // create function to draw the arcs of the pie slices.
                    var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

                    // create a function to compute the pie slice angles.
                    var pie = d3.layout.pie().sort(null).value(function (d) { return d.enquiry; });

                    // Draw the pie slices.
                    piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
                        .each(function (d) { this._current = d; })
                        .attr("fill", function (d, i) { return color(i); })
                        .on("mouseover", mouseover).on("mouseout", mouseout);

                    // create function to update pie-chart. This will be used by histogram.
                    pC.update = function (nD) {
                        piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                            .attrTween("d", arcTween);
                    }
                    // Utility function to be called on mouseover a pie slice.
                    function mouseover(d, i) {
                        // call the update function of histogram with new data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.enquiry[d.data.type]];
                        }), color(i));
                    }
                    //Utility function to be called on mouseout a pie slice.
                    function mouseout(d) {
                        // call the update function of histogram with all data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.total];
                        }), barColor);

                    }
                    // Animating the pie-slice requiring a custom function which specifies
                    // how the intermediate paths should be drawn.
                    function arcTween(a) {
                        var i = d3.interpolate(this._current, a);
                        this._current = i(0);
                        return function (t) { return arc(i(t)); };
                    }
                    return pC;
                }

                // function to handle legend.
                function legend(lD) {
                    var leg = {};

                    // create table for legend.
                    var legend = d3.select(id).append("table").attr('class', 'legend');

                    // create one row per segment.
                    var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");

                    // create the first column for each segment.
                    tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                        .attr("width", '16').attr("height", '16')
                        .attr("fill", function (d, i) { return color(i); })

                    // create the second column for each segment.
                    tr.append("td").text(function (d) { return d.type; });

                    // create the third column for each segment.
                    tr.append("td").attr("class", 'legendFreq')
                        .text(function (d) { return d.l_month; });

                    // create the fourth column for each segment.
                    tr.append("td").attr("class", 'legendPerc')
                        .text(function (d) { return getLegend(d, lD); });

                    // Utility function to be used to update the legend.
                    leg.update = function (nD) {
                        // update the data attached to the row elements.
                        var l = legend.select("tbody").selectAll("tr").data(nD);

                        // update the frequencies.
                        l.select(".legendFreq").text(function (d) { return d3.format(",")(d.enquiry); });

                        // update the percentage column.
                        l.select(".legendPerc").text(function (d) { return getLegend(d, nD); });
                    }

                    function getLegend(d, aD) { // Utility function to compute percentage.
                        var perc = (d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        if (isNaN(perc)) {
                            return d3.format("%")(0);
                        }
                        else {
                            return d3.format("%")(d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        }
                    }

                    return leg;
                }
                // calculate total frequency by segment for all state.
                var tF = dept.map(function (d) {
                    return { type: d, enquiry: d3.sum(fData.map(function (t) { return t.enquiry[d]; })) };
                });

                // calculate total frequency by state for all segment.
                var sF = fData.map(function (d) { return [d.l_month, d.total]; });

                var hG = histoGram(sF), // create the histogram.
                    pC = pieChart(tF), // create the pie-chart.
                    leg = legend(tF);  // create the legend.
            });
        },
        render_enquiry_weekly_graph: function () {
            var self = this;
            //        var color = d3.scale.category10();
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337', '#fe7139',
                '#ffa433', '#ffc25b', '#f8e54b'];
            var color = d3.scale.ordinal().range(colors);
            rpc.query({
                model: "airport.enquiry",
                method: "get_the_weekly_enquiry",
            }).then(function (data) {
                var fData = data[0];
                var dept = data[1];
                var id = self.$('.enquiry_graph_week')[0];
                var barColor = '#ff618a';
                fData.forEach(function (d) {
                    var total = 0;
                    for (var dpt in dept) {
                        total += d.enquiry[dept[dpt]];
                    }
                    d.total = total;
                });

                // function to handle histogram.
                function histoGram(fD) {
                    var hG = {}, hGDim = { t: 60, r: 0, b: 30, l: 0 };
                    hGDim.w = 350 - hGDim.l - hGDim.r,
                        hGDim.h = 200 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                        .domain(fD.map(function (d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                        .domain([0, d3.max(fD, function (d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                        .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function (d) { return x(d[0]); })
                        .attr("y", function (d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function (d) { return hGDim.h - y(d[1]); })
                        .attr('fill', barColor)
                        .on("mouseover", mouseover)// mouseover is defined below.
                        .on("mouseout", mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function (d) { return d3.format(",")(d[1]) })
                        .attr("x", function (d) { return x(d[0]) + x.rangeBand() / 2; })
                        .attr("y", function (d) { return y(d[1]) - 5; })
                        .attr("text-anchor", "middle");

                    function mouseover(d) {  // utility function to be called on mouseover.
                        // filter for selected state.
                        var st = fData.filter(function (s) { return s.l_month == d[0]; })[0],
                            nD = d3.keys(st.enquiry).map(function (s) { return { type: s, enquiry: st.enquiry[s] }; });

                        // call update functions of pie-chart and legend.
                        pC.update(nD);
                        leg.update(nD);
                    }

                    function mouseout(d) {    // utility function to be called on mouseout.
                        // reset the pie-chart and legend.
                        pC.update(tF);
                        leg.update(tF);
                    }

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function (nD, color) {
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function (d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function (d) { return y(d[1]); })
                            .attr("height", function (d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function (d) { return d3.format(",")(d[1]) })
                            .attr("y", function (d) { return y(d[1]) - 5; });
                    }
                    return hG;
                }

                // function to handle pieChart.
                function pieChart(pD) {
                    var pC = {}, pieDim = { w: 250, h: 250 };
                    pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;

                    // create svg for pie chart.
                    var piesvg = d3.select(id).append("svg")
                        .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
                        .attr("transform", "translate(" + pieDim.w / 2 + "," + pieDim.h / 2 + ")");

                    // create function to draw the arcs of the pie slices.
                    var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

                    // create a function to compute the pie slice angles.
                    var pie = d3.layout.pie().sort(null).value(function (d) { return d.enquiry; });

                    // Draw the pie slices.
                    piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
                        .each(function (d) { this._current = d; })
                        .attr("fill", function (d, i) { return color(i); })
                        .on("mouseover", mouseover).on("mouseout", mouseout);

                    // create function to update pie-chart. This will be used by histogram.
                    pC.update = function (nD) {
                        piesvg.selectAll("path").data(pie(nD)).transition().duration(500)
                            .attrTween("d", arcTween);
                    }
                    // Utility function to be called on mouseover a pie slice.
                    function mouseover(d, i) {
                        // call the update function of histogram with new data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.enquiry[d.data.type]];
                        }), color(i));
                    }
                    //Utility function to be called on mouseout a pie slice.
                    function mouseout(d) {
                        // call the update function of histogram with all data.
                        hG.update(fData.map(function (v) {
                            return [v.l_month, v.total];
                        }), barColor);

                    }
                    // Animating the pie-slice requiring a custom function which specifies
                    // how the intermediate paths should be drawn.
                    function arcTween(a) {
                        var i = d3.interpolate(this._current, a);
                        this._current = i(0);
                        return function (t) { return arc(i(t)); };
                    }
                    return pC;
                }

                // function to handle legend.
                function legend(lD) {
                    var leg = {};

                    // create table for legend.
                    var legend = d3.select(id).append("table").attr('class', 'legend');

                    // create one row per segment.
                    var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");

                    // create the first column for each segment.
                    tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                        .attr("width", '16').attr("height", '16')
                        .attr("fill", function (d, i) { return color(i); })

                    // create the second column for each segment.
                    tr.append("td").text(function (d) { return d.type; });

                    // create the third column for each segment.
                    tr.append("td").attr("class", 'legendFreq')
                        .text(function (d) { return d.l_month; });

                    // create the fourth column for each segment.
                    tr.append("td").attr("class", 'legendPerc')
                        .text(function (d) { return getLegend(d, lD); });

                    // Utility function to be used to update the legend.
                    leg.update = function (nD) {
                        // update the data attached to the row elements.
                        var l = legend.select("tbody").selectAll("tr").data(nD);

                        // update the frequencies.
                        l.select(".legendFreq").text(function (d) { return d3.format(",")(d.enquiry); });

                        // update the percentage column.
                        l.select(".legendPerc").text(function (d) { return getLegend(d, nD); });
                    }

                    function getLegend(d, aD) { // Utility function to compute percentage.
                        var perc = (d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        if (isNaN(perc)) {
                            return d3.format("%")(0);
                        }
                        else {
                            return d3.format("%")(d.enquiry / d3.sum(aD.map(function (v) { return v.enquiry; })));
                        }
                    }

                    return leg;
                }
                // calculate total frequency by segment for all state.
                var tF = dept.map(function (d) {
                    return { type: d, enquiry: d3.sum(fData.map(function (t) { return t.enquiry[d]; })) };
                });

                // calculate total frequency by state for all segment.
                var sF = fData.map(function (d) { return [d.l_month, d.total]; });

                var hG = histoGram(sF), // create the histogram.
                    pC = pieChart(tF), // create the pie-chart.
                    leg = legend(tF);  // create the legend.
            });
        },


        //    Actions
        action_my_customers: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Customers"),
                type: 'ir.actions.act_window',
                res_model: 'res.partner',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['company_type', '=', 'person'], ['company_name', '=', false]],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        action_my_airports: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Airports"),
                type: 'ir.actions.act_window',
                res_model: 'admin.airport',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        action_my_enquires: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Enquires"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        action_my_new_enquires: function (event) {
            var self = this;
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
            var yyyy = today.getFullYear();

            today = dd + '/' + mm + '/' + yyyy;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("New Enquires"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['status', '=', 'new']],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        //    action_my_upcoming_enquires: function(event) {
        //        var self = this;
        //        var today = new Date();
        //        var dd = String(today.getDate()).padStart(2, '0');
        //        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        //        var yyyy = today.getFullYear();
        //
        //        today = dd + '/' + mm + '/' + yyyy;
        //        event.stopPropagation();
        //        event.preventDefault();
        //        this.do_action({
        //            name: _t("Upcoming Enquires"),
        //            type: 'ir.actions.act_window',
        //            res_model: 'airport.enquiry',
        //            view_mode: 'tree,form',
        //            view_type: 'form',
        //            views: [[false, 'list'],[false, 'form']],
        //            domain: [['service_date','>=',today],['payment_done','=',false]],
        //            target: 'current'
        //        },{on_reverse_breadcrumb: function(){ return self.reload();}})
        //    },
        action_my_upcoming_services: function (event) {
            var self = this;
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
            var yyyy = today.getFullYear();

//             for server
            today = yyyy + '/' + mm + '/' + dd;
//             for local
//            today = dd + '/' + mm + '/' + yyyy;

            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Upcoming Services"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['service_date', '>=', today], ['payment_done', '=', true],['status', '=', 'open'],['response_status','=','confirmation_voucher_send']],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        action_my_open_enquires: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Open Enquires"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['status', '=', 'open']],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        action_my_close_enquires: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Closed Enquires"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['status', '=', 'close']],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },

        action_my_cancelled_enquires: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Cancelled Enquires"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['response_status', '=', 'cancelled']],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },
        action_my_paid_enquires: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action({
                name: _t("Paid Enquires"),
                type: 'ir.actions.act_window',
                res_model: 'airport.enquiry',
                view_mode: 'tree,form',
                view_type: 'form',
                views: [[false, 'list'], [false, 'form']],
                domain: [['payment_status', '=', 'paid'],['status', '!=', 'close']],
                target: 'current'
            }, { on_reverse_breadcrumb: function () { return self.reload(); } })
        },

    });
    core.action_registry.add('uaa_dashboard', UAADashboardView);
    return UAADashboardView

});
