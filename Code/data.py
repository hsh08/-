import requests
import xml.etree.ElementTree as ET

# 제공받은 API 인증키 (Decoding 된 값 사용)
api_key = "SmwjDkJ6papY5wbYOdj+gJiviVC9HBwTZyYSkQr8U25DFky5q1712c9K3dZJE+VML8zE88kREgQ9wkVSmzDxuA=="

# API 요청 기본 URL
base_url = "https://apis.data.go.kr/1520635/OceanProblemService/getOceanproblemRedTideOccurrenceInfo"

# 요청 변수 설정 - 더 많은 연도의 데이터를 얻기 위해 numOfRows를 늘려봅니다.
# API가 허용하는 최대치나 적절한 값을 설정하세요. (예: 100, 200, 500 등)
params = {
    'serviceKey': api_key,
    'numOfRows': '300',  # <-- 데이터 개수를 늘려봅니다. (필요에 따라 조정)
    'pageNo': '1',
    # 'rdate': 'YYYYMMDD' # 특정 날짜를 조회하고 싶다면 주석 해제하고 날짜 입력
}

print(f"실제 API 요청 URL: {requests.Request('GET', base_url, params=params).prepare().url}")
print(f"요청 파라미터: {params}")

try:
    # API 호출
    response = requests.get(base_url, params=params)
    print(f"HTTP 응답 상태 코드: {response.status_code}")
    response.raise_for_status() # HTTP 오류 발생 시 예외 발생

    # 응답 데이터 (XML 형식)
    xml_data = response.text

    # XML 데이터 파싱
    root = ET.fromstring(xml_data)

    # 결과 코드 및 메시지 확인
    result_code_element = root.find('.//resultCode')
    result_msg_element = root.find('.//resultMsg')
    total_count_element = root.find('.//totalCount')

    result_code = result_code_element.text if result_code_element is not None else 'N/A'
    result_msg = result_msg_element.text if result_msg_element is not None else 'N/A'
    total_count = total_count_element.text if total_count_element is not None else 'N/A'

    print(f"\n결과 코드: {result_code}")
    print(f"결과 메시지: {result_msg}")
    print(f"전체 데이터 개수 (<totalCount>): {total_count}")

    if result_code == '00': # 결과 코드가 '00'이면 성공
        items = root.findall('.//item')
        print(f"응답에서 파싱된 <item> 개수: {len(items)}")

        if items:
            # --- HTML 시작 부분 (그래프 관련 CSS 및 Chart.js CDN 포함) ---
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>적조 정보 - 테이블과 그래프</title>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                /* 여러 개의 그래프를 담을 컨테이너 */
                #yearlyCharts {
                    display: flex;
                    flex-wrap: wrap; /* 공간 부족 시 줄 바꿈 */
                    gap: 30px; /* 그래프 간 간격 */
                    justify-content: center; /* 가운데 정렬 */
                    margin-top: 40px;
                }
                .chart-container { /* 각 그래프를 감싸는 div */
                     width: 45%; /* 각 그래프 컨테이너의 너비 (조정 가능) */
                     max-width: 600px; /* 최대 너비 설정 */
                     margin-bottom: 20px; /* 그래프 아래 여백 */
                     border: 1px solid #eee; /* 그래프 영역 구분선 */
                     padding: 15px;
                     box-sizing: border-box; /* 패딩 포함 크기 계산 */
                     background-color: #fff;
                     box-shadow: 2px 2px 5px rgba(0,0,0,0.1); /* 그림자 효과 */
                }
                .chart-container canvas {
                    width: 100% !important; /* 부모 div에 맞게 너비 조절 */
                    height: 300px !important; /* 높이 고정 (조정 가능) */
                }
            </style>
            <!-- Chart.js 라이브러리 추가 -->
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
            <h1>적조 발생 정보</h1>

            <table>
            <thead>
            <tr>
            <th>발생 날짜</th>
            <th>속보 코드</th>
            <th>제목</th>
            <th>진행 상태</th>
            <th>금후 전망</th>
            <th>당부 사항</th>
            <th>특보 사항</th>
            </tr>
            </thead>
            <tbody>
            """

            # --- 테이블 행 추가 (파이썬에서 데이터 읽어서 동적으로 생성) ---
            for item in items:
                rdate = item.find('rdate').text if item.find('rdate') is not None else ''
                srcode = item.find('srcode').text if item.find('srcode') is not None else ''
                title = item.find('title').text if item.find('title') is not None else ''
                pstate = item.find('pstate').text if item.find('pstate') is not None else ''
                aview = item.find('aview').text if item.find('aview') is not None else ''
                etc = item.find('etc').text if item.find('etc') is not None else ''
                sreport = item.find('sreport').text if item.find('sreport') is not None else ''

                html_content += f"""
                <tr>
                    <td>{rdate}</td>
                    <td>{srcode}</td>
                    <td>{title}</td>
                    <td>{pstate}</td>
                    <td>{aview}</td>
                    <td>{etc}</td>
                    <td>{sreport}</td>
                </tr>
                """

            # --- HTML 마무리 및 JavaScript 코드 추가 ---
            html_content += """
            </tbody>
            </table>

            <!-- 연도별 그래프들을 담을 영역 -->
            <div id="yearlyCharts">
                <!-- JavaScript 코드에서 여기에 각 연도별 그래프가 추가됩니다 -->
            </div>

            <script>
                // HTML 문서가 완전히 로드된 후 JavaScript 실행
                document.addEventListener('DOMContentLoaded', () => {
                    // HTML 테이블에서 날짜 데이터 읽기
                    const rows = document.querySelectorAll('table tbody tr');
                    const data = [];

                    rows.forEach(row => {
                        const dateCell = row.cells[0]; // 첫 번째 셀 (날짜)
                        if (dateCell) {
                            const dateText = dateCell.textContent.trim();
                            if(dateText.length === 8) { // YYYYMMDD 형식 확인
                                const year = dateText.substring(0,4);
                                const month = parseInt(dateText.substring(4,6), 10);
                                data.push({year, month});
                            }
                        }
                    });

                    // 연도별 월별 집계
                    const counts = {};
                    data.forEach(({year, month}) => {
                        if(!counts[year]) counts[year] = {};
                        counts[year][month] = (counts[year][month] || 0) + 1;
                    });

                    // 연도별로 그래프 그리기
                    const yearlyChartsContainer = document.getElementById('yearlyCharts');
                    const years = Object.keys(counts).sort(); // 연도 순으로 정렬

                    years.forEach(year => {
                        // 각 연도별 그래프를 담을 컨테이너 div 생성
                        const chartContainerDiv = document.createElement('div');
                        chartContainerDiv.className = 'chart-container'; // CSS 클래스 적용
                        yearlyChartsContainer.appendChild(chartContainerDiv);

                        // 각 연도별 canvas 요소 생성
                        const chartCanvas = document.createElement('canvas');
                        chartCanvas.id = `chart-${year}`; // 고유 ID 부여
                        chartContainerDiv.appendChild(chartCanvas); // 컨테이너 div 안에 canvas 추가

                        const ctx = chartCanvas.getContext('2d');

                        // 해당 연도의 월별 데이터 준비 (1월부터 12월까지)
                        const months = Array.from({length: 12}, (_, i) => i + 1); // [1, 2, ..., 12]
                        const monthlyCounts = months.map(m => counts[year] ? counts[year][m] || 0 : 0); // 해당 연도 데이터 없을 경우 처리

                        // Chart.js 막대 그래프 생성
                        new Chart(ctx, {
                            type: 'bar',
                            data: {
                                labels: months.map(m => m + '월'),
                                datasets: [{
                                    label: `${year}년 발생 건수`, // 데이터셋 레이블
                                    data: monthlyCounts,
                                    backgroundColor: 'rgba(75, 192, 192, 0.6)', // 색상 변경
                                    borderColor: 'rgba(75, 192, 192, 1)',
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: { stepSize: 1 },
                                        title: { display: true, text: '발생 건수' }
                                    },
                                    x: {
                                        title: { display: true, text: '월' }
                                    }
                                },
                                plugins: {
                                    legend: { display: true },
                                    title: { display: true, text: `${year}년 월별 적조 발생 건수` } // 차트 제목
                                },
                                responsive: true,
                                maintainAspectRatio: false // 부모 컨테이너 크기에 맞게 조절
                            }
                        });
                    });
                }); // DOMContentLoaded 끝
            </script>

            </body>
            </html>
            """

            # HTML 파일로 저장
            with open('redtide_data.html', 'w', encoding='utf-8') as f:
                f.write(html_content)

            print("\n데이터를 'redtide_data.html' 파일로 성공적으로 저장했습니다.")
            print(f"총 {len(items)} 건의 데이터를 HTML 테이블에 포함했습니다.")

        else:
            print("\n조회된 적조 정보가 없습니다.")

    else:
        print("\nAPI 호출에 실패했습니다.")
        print(f"오류 코드: {result_code}")
        print(f"오류 메시지: {result_msg}")

except requests.exceptions.RequestException as e:
    print(f"API 호출 중 오류 발생: {e}")
except ET.ParseError as e:
    print(f"XML 파싱 중 오류 발생: {e}")
except Exception as e:
    print(f"예상치 못한 오류 발생: {e}")
