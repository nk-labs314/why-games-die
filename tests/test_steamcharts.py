from game_decline.steam.steamcharts import parse_monthly_table, rows_to_csv


SAMPLE_HTML = """
<html>
  <body>
    <table class="common-table">
      <tr>
        <th>Month</th>
        <th>Avg. Players</th>
        <th>Gain</th>
        <th>% Gain</th>
        <th>Peak Players</th>
      </tr>
      <tr>
        <td>April 2026</td>
        <td>13,837.4</td>
        <td>-1,503.2</td>
        <td>-9.80%</td>
        <td>25,132</td>
      </tr>
      <tr>
        <td>March 2026</td>
        <td>15,340.6</td>
        <td>+102.0</td>
        <td>+0.67%</td>
        <td>27,900</td>
      </tr>
    </table>
  </body>
</html>
"""


def test_parse_monthly_table_extracts_numeric_rows():
    rows = parse_monthly_table(570, SAMPLE_HTML)

    assert len(rows) == 2
    assert rows[0].app_id == 570
    assert rows[0].month == "April 2026"
    assert rows[0].avg_players == 13837.4
    assert rows[0].gain == -1503.2
    assert rows[0].percent_gain == -9.8
    assert rows[0].peak_players == 25132


def test_rows_to_csv_preserves_expected_columns():
    csv_text = rows_to_csv(parse_monthly_table(570, SAMPLE_HTML))

    assert csv_text.splitlines()[0] == "app_id,month,avg_players,gain,percent_gain,peak_players"
    assert "570,April 2026,13837.4,-1503.2,-9.8,25132" in csv_text
