import os.path

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from config.errorCode import errors
from PyQt5.QtTest import QTest
from config.kiwoomType import RealType
# QaxWidget 파이썬 파일중 컨테이너부분을 직접적으로 접근할수 있는 API로 서비스.서비스임플.맵퍼.DB (구현부안에 상속된건 아님) 추정됨.
class Kiwoom(QAxWidget):

    """
    https://wikidocs.net/5755
    키움증권에서로 부터 설치한것은 OCX 방식에 컨포넌트 객체로 설치가 되었다.
    응용프로그램에서 키움Open API를 실행 할 수 있게 한거다.
    덕분에 제어가 된다.
    제어 할수 있는 함수는 PytQ5
    시그널 = 요청
    키움 API는 싱글데이터 멀티데이터 Key제목을 꼭 보고 가져와야 된다.
    """

    def __init__(self):

        super().__init__() # 분모에있는 초기값들을 사용하기위해 분모에 있는 init을 사용한다.

        print("키움 API 연동")

        self.realType = RealType()

        ############event_loop
        self.login_exec         = None
        ######################

        ############변수모음###
        self.account_BankNum    = None # 계좌번호
        self.sPrevNext          = None # 페이지 번호
        self.checkBalanceBox    = {} # 계좌잔고 계좌종목
        self.not_tighteningBox  = {} # 미체결
        #####################

        ###########종합일봉리스트########
        self.onedaypayListData = [] # 모든 데이터 리스트(중점데이터)
        ###############################

        #############스크린 번호 모음
        self.QscreenNumberT     = 2000
        self.QscreenNumberF     = 4000
        self.QscreenNumberFi    = 5000
        self.QscreenNumberS     = 6000
        self.realTime_start_stop_QscreenNumberO = 1000

        ############유저 계좌 접근 변수
        self.userMoney          = None
        self.deposit_persent    = 0.5
        self.deposit_division   = 4
        ###########################

        #############이벤트 루프 모음
        self.defult_account_info_event_loop = QEventLoop()
        ###########################################

        ##############조건선별 file변수###
        self.files_stock_diet = {}
        ###############################

        self.get_Ocx_Install()
        self.event_slot_List()

        self.signal_login_CommConnect()
        self.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
        self.get_account_info()

        # 예수금 조회
        self.deposit_acount_info()

        # 계좌평가잔고내역요청 조회
        self.checkBalance_acount_info()

        # 종목분석용, 임시용으로 실행
        self.calculator_Fn()

        # condition_stock.txt에 저장된 종목들을 불러옵니다.
        self.read_code()

        print("계좌번호 :%s" % self.account_BankNum)
        print("페이지 번호 :%s" % self.sPrevNext)
        print("계좌잔고 계좌종목 :%s" % self.checkBalanceBox)
        print("미체결 :%s" % self.not_tighteningBox)
        print("조건선별딕셔너리 :%s" % self.files_stock_diet)

        # 각각의 스크린번호 Setting
        self.screen_number_settings()

        """
        0 : 처음 RealTime 등록했을시
        1 : 이후 추가 RealTime 등록시
        """

        # realTypeData Test
        print(self.realType.REALTYPE['장시작시간']['장운영구분'])
        print(self.realType.REALTYPE['장시작시간']['시간'])

        self.real_slot_call()
        # RealTime_slot_Insert
        self.real_slot_event()

    def get_Ocx_Install(self):

        """
        키움 API를 설치함으로써 응용프로그램들이 우리 window 레지스트리에 저장된다.
        레지스트리 편집기에 찾을수 있다.
        KHOPENAPI.KHOpenAPICtrl.1 폴더명으로 저장되며 DKHOPENAPI 기본값으로 설정되어있다.
        """

        # 응용프로그램을 제어하기 위한 그 설치된 경로를 지정해주어야됨
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slot_List(self):

        # 로그인용 이벤트 슬롯연결
        self.OnEventConnect.connect(self.login_slot)

        # TR용 이벤트 슬롯연결
        self.OnReceiveTrData.connect(self.trData_slot)

    # 0503 Testing Error
    def real_slot_event(self):

        self.OnReceiveRealData.connect(self.realData_slot)

    # 로그인 성공시 이벤트
    def login_Function(self, nErrCode):
        print('로그인처리 %d' % nErrCode)

        self.login_exec.exit()

    # 키움 로그인 기능창 출력 or 자동설정 (로그인 시도)
    def signal_login_CommConnect(self):

        """
         로그인 성공시에 대한 이벤트 지정을 안해주면 로그인 성공시에 이벤트값이 없기에
         이벤트 핸들러 오류 발생할수 있음
        """

        # 네트워크적이거나 다른 서버 응용프로그램에다가 데이터를 전송할수 있음음
        self.dynamicCall("CommConnect()")

        # QtCore 이벤트 루프 초기화
        self.login_exec = QEventLoop()

        # 이벤트 루프 지정
        self.login_exec.exec_()

    # 키움 에러처리 key
    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_exec.exit()

    # 계좌번호가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(QString)","ACCLIST")

        # split : 문자열 자르기 (계좌번호 가져올때 18545454545;45447878785; 이런식으로 출력됨)
        self.account_BankNum = account_list.split(';')[0]

        # 현재 계좌번호
        print('현재 계좌 번호 %s' % self.account_BankNum)

    # 예수금 요청내역
    def deposit_acount_info(self):
        print('예수금 조회 요청')

        # 조회 함수입력
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_BankNum) # 계좌번호
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", '2') #2는 일반조회 3은 추정조회

        # 예수금 상세현황요청 조회함수 호출하여 서버전송
        self.dynamicCall("CommRqData(QString, QString, QString, QString)", "예수금상세현황요청", "opw00001",
                         '0', self.QscreenNumberT)

        # 다른데이터를 처리하는동안 다른작업을 할수있게 만드는것 이벤트 루프
        self.defult_account_info_event_loop
        self.defult_account_info_event_loop.exec_()

    # 계좌평가잔고내역요청내역, sPrevNext값이 0으로 설정되었기에 싱글데이터값을 요청함함
    def checkBalance_acount_info(self, setsPrevNext = "0"):
        print("계좌평가잔고내역요청")

        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_BankNum)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", '2')

        # 계좌평가잔고내역요청 조회함수 호출하여 서버전송
        self.dynamicCall("CommRqData(QString, QString, QString, QString)", "계좌평가잔고내역요청", "opw00018",
                         setsPrevNext, self.QscreenNumberF)

        self.defult_account_info_event_loop.exec_()

    # 미체결요청
    def not_tightening_acount_info(self):
        print("미체결요청")

        # 조회하고 싶은것만 받아오게 할수있다.
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호",self.account_BankNum)
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", 0)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", 1)

        # Kiwoom서버에게 해당 데이터값 요청
        self.dynamicCall("CommRqData(QString, QString, QString, QString)", "미체결요청", "opt10075", 0,
                         self.QscreenNumber)

        self.defult_account_info_event_loop.exec_()

    # 주식일봉차트조회요청
    def request_to_check_the_stock_pay_chart(self, eventCode = None, date = None, setsPrevNext = 0):
        print("주식일봉차트조회")

        """
        위 네트워크적인 프로세스를 멈추진 않고 대신에 이상태에서 다음 코드실행하기 전에 4초 지연합니다. (보안상 3.5초 이상 지연)
        너무 느리지만 이점을 보완할 방법이 딱히 없다.
        그리고 키움은 매일 새벽마다 업데이트를 한다.
        """
        QTest.qWait(4000)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", eventCode)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회",
                         "opt10081", setsPrevNext, self.QscreenNumberF) #TR서버로 전송

        self.defult_account_info_event_loop.exec_()

    def get_code_list_by_market(self, market_code):
        '''
        종목코드들 반환
        :param market_code:
        :return:
        '''

        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]

        return code_list

    def calculator_Fn(self):

        code_list = self.get_code_list_by_market("10")
        print("코스닥 갯수 %s", len(code_list))

        # 데이터가 너무 많아 1449이기에 3개로 줄여서 테스팅실시함.
        for index, code in enumerate(code_list[0:3]):

            """
            추가 : 스크린번호를 한번이라도 요청하면 그룹이 만들어 진것이다.
            그래서 끊어주는건 개인의 선택이다.
            """
            # 화면번호 끊기
            self.dynamicCall("DisconnectRealData(QString)", self.QscreenNumberF)
            print ("%s / %s : Kosdaq code_list : %s" % (index+1, len(code_list), code))
            self.request_to_check_the_stock_pay_chart(eventCode = code)


    # Tr슬롯

    def trData_slot(self, sScrNo, sRQName, sTrCode,sRecordName,sPrevNext):
        '''
        TR 요청을 받는 구역 (슬롯)
        :param sScrNo: 화면번호
        :param sRQName: 사용자 구분명
        :param sTrCode: TR이름
        :param sRecordName: 레코드이름
        :param sPrevNext: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음 (다음페이지가 있는지)
        sPrevNext는 다음페이지가 활성화가 되면 2로 반환됩니다. 만약 다음페이지가 비활성화 상태라면 첫페이지인 0 or ""이 반환됩니다.
        다음페이지 활성화조건은 계좌평가잔고내역요청에 종목코드가 20개 초과일시 생성되어야합니다.
        :return:
        '''

        print(sTrCode)

        if (sRQName == "예수금상세현황요청"):

            """
            GetCommData
            - OnReceiveTRData()이벤트가 발생될때 수신한 데이터를 얻어오는 함수입니다.
            이 함수는 OnReceiveTRData()이벤트가 발생될때 그 안에서 사용해야 합니다.
            """

            # TR이름, 레코드이름인데 사용자 구분명으로 대체함;, 0은 아직도 잘 모르겠다, 필드항목이름이 예수금임
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName,
                                       0, "예수금")
            print(deposit)
            print("예수금 : %s" % deposit)
            print("예수금 형변환 : %s" % int(deposit))

            ###### 유저 한번 구입할때 조절하는 수치 (고객이 직접조절하게 GUI 개선해야됨)
            self.userMoney = int(deposit) * self.deposit_persent
            self.userMoney = self.userMoney / self.deposit_division

            stock_evidence_cash = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode,
                                                   sRQName, 0, "주식증거금현금")
            print("주식증거금현금 : %s" % stock_evidence_cash)
            print("주식증거금현금 형변환 : %s" % int(stock_evidence_cash))

            ture_deposit = self.dynamicCall("GetCommData(QString, QString, QString, QString)", sTrCode,
                                            sRQName, 0, "출금가능금액")
            print("출금가능금액 : %s" % ture_deposit)
            print("출금가능금액 형변환 : %d" % int(ture_deposit))

            self.defult_account_info_event_loop.exit()

        elif (sRQName == "계좌평가잔고내역요청"):

            # 계좌평가잔고내역요청_총매입금액
            checkBalance_total_purchase_amount = self.dynamicCall("GetCommData(QString, QString, QString, QString)",
                                                                  sTrCode, sRQName, 0, "총매입금액")
            print('총매입금액 : %s' % checkBalance_total_purchase_amount)
            print('총매입금액 형변환 : %s' % int(checkBalance_total_purchase_amount))

            # 계좌평가잔고내역요청_총평가금액
            checkBalance_total_evaluation_amount = self.dynamicCall("GetCommData(QString, QString, QString, QString)",
                                                                    sTrCode, sRQName, 0, "총평가금액")
            print('총평가금액 : %s' % checkBalance_total_evaluation_amount)
            print('총평가금액 형변환 : %s' % int(checkBalance_total_evaluation_amount))

            # 계좌평가잔고내역요청_총수익률
            checkBalance_yield = self.dynamicCall("GetCommData(QString, QString, QString, QString)",
                                                  sTrCode, sRQName, 0, "총수익률(%)")
            print('총수익률(%%) : %s' % checkBalance_yield)
            print('총수익률(%%) 형변환 : %s' % float(checkBalance_yield),'%')

            # 현재 주식 매매 카운트 (GetRepeatCnt를 사용하면 카운트가 멀티데이터로 됨)
            cint = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            # 종목이 몇개 인지 뽑아보기 위해서 함

            # 600일의 관한 일봉 데이터
            for i in range(cint):

                balance_id                  = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "종목번호")
                balance_item_nm             = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "종목명")
                balance_retained_quantity   = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "보유수량")
                balance_purchase_price      = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "매입가")
                balance_yield               = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "수익률(%)")
                balance_current_price       = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "현재가")
                balance_purchase_amount     = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "매입금액")
                balance_tradeable_quantity  = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                               sTrCode, sRQName, i, "매매가능수량")

                # checkBalance 안에 cint이 있다면
                if (cint in self.checkBalanceBox):
                    pass

                else:

                    # self.checkBalanceBox[balance_id] = {} 이렇게 사용해도됨
                    balance_id = balance_id.strip()[1:]
                    self.checkBalanceBox.update({balance_id: {}})

                # strip(공백없애기) 하지만 [1:] 이면 2번째요소(인덱스자리 1)부터 시작한다는뜻
                balance_item_nm             = balance_item_nm.strip()
                balance_retained_quantity   = int(balance_retained_quantity.strip())
                balance_purchase_price      = int(balance_purchase_price.strip())
                balance_yield               = float(balance_yield.strip())
                balance_current_price       = int(balance_current_price.strip())
                balance_purchase_amount     = int(balance_purchase_amount.strip())
                balance_tradeable_quantity  = int(balance_tradeable_quantity.strip())

                checkBalanceBoxSkip = self.checkBalanceBox[balance_id]

                # 종목 코드 해당 id 딕셔너리 안에 그 안에 딕셔너리 추가함
                checkBalanceBoxSkip.update({"종목명": balance_item_nm})
                checkBalanceBoxSkip.update({"보유수량": balance_retained_quantity})
                checkBalanceBoxSkip.update({"매입가": balance_purchase_price})
                checkBalanceBoxSkip.update({"수익률(%)": balance_yield})
                checkBalanceBoxSkip.update({"현재가": balance_current_price})
                checkBalanceBoxSkip.update({"매입금액": balance_purchase_amount})
                checkBalanceBoxSkip.update({"매매가능수량": balance_tradeable_quantity})

                print("종목코드: %s - 종목명: %s - 보유수량: %s - 매입가:%s - 수익률: %s - 현재가: %s" %
                      (balance_id, balance_item_nm, balance_retained_quantity, balance_purchase_price, balance_yield,
                       balance_current_price))

                print("계좌 가지고 있는종목 : %d" % len(self.checkBalanceBox))

                if (sPrevNext == "2"):

                    self.checkBalance_acount_info(setsPrevNext = "2")

                else:

                    self.defult_account_info_event_loop.exit()

            print(self.checkBalanceBox.keys())
            print(self.checkBalanceBox.values())

        elif (sRQName == "미체결요청"):

            # 미체결요청에 GetRepeatCnt은 최대 100Count
            not_tightening_List = self.dynamicCall("GetRepeatCnt(QStirng, QString)", sTrCode, sRQName)

            for i in range(not_tightening_List):
                not_tightening_id                = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "종목코드")
                not_tightening_nm                = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "종목명")

                # -매도 +매수, -매도정리
                not_tightening_order_sortation   = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "주문구분")

                # 접수 -> 확인 -> 체결
                not_tightening_order_state       = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "주문상태")

                not_tightening_order_quantity    = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "주문수량")
                not_tightening_order_price       = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "주문가격")

                # 기본키
                not_tightening_order_no          = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "주문번호")

                not_tightening_quantity          = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "미체결수량")
                tightening_quantity              = self.dynamicCall("GetCommData(QString QString int QString)",
                                                                    sTrCode, sRQName, i, "체결량")

                not_tightening_id = not_tightening_id.strip()
                not_tightening_nm = not_tightening_nm.strip()

                # 첫문자 + or - 를 제거
                not_tightening_order_sortation  = not_tightening_order_sortation.strip().lstrip('+').lstrip('-')
                not_tightening_order_state      = not_tightening_order_state.strip()
                not_tightening_order_quantity   = int(not_tightening_order_quantity.strip())
                not_tightening_order_price      = int(not_tightening_order_price.strip())
                not_tightening_order_no         = int(not_tightening_order_no.strip())
                not_tightening_quantity         = int(not_tightening_quantity.strip())
                tightening_quantity             = int(tightening_quantity.strip())


                if not_tightening_order_no in self.not_tighteningBox:
                    pass

                else:

                    self.not_tighteningBox.update({not_tightening_order_no,{}})

                not_tighteningBox_skip = self.not_tighteningBox[not_tightening_order_no]

                not_tighteningBox_skip.update({"종목코드", not_tightening_id})
                not_tighteningBox_skip.update({"종목명", not_tightening_nm})
                not_tighteningBox_skip.update({"주문구분", not_tightening_order_sortation})
                not_tighteningBox_skip.update({"주문상태", not_tightening_order_state})
                not_tighteningBox_skip.update({"주문수량", not_tightening_order_quantity})
                not_tighteningBox_skip.update({"주문가격", not_tightening_order_price})
                not_tighteningBox_skip.update({"미체결수량", not_tightening_quantity})
                not_tighteningBox_skip.update({"체결량", tightening_quantity})

                print("미체결 관련 데이터 %s" % self.not_tighteningBox)

        elif "주식일봉차트조회" == sRQName:

            """
            장기적인 투자면 이방법이 편하지만 단기적으로 해야된다면 이방법은 추천드리지 않는다.
            문제점 방대한 데이터를 전부 instoll하기엔 너무 오래걸린다.
            그렇기에 특정 종목코드를 지정하거나 데이터수를 리미트를 걸어서 가져온다.
            """

            # 싱글데이터
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            # 최대 호출 카운트
            cint = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("데이터 일수 %s" % cint)

            # 하루치들의 데이터들 600번 반복
            for i in range(cint):

                data = []

                current_price       = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                 sTrCode, sRQName, i, "현재가") #종가
                transaction_volume  = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                      sTrCode, sRQName, i, "거래량")
                transaction_amount  = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                      sTrCode, sRQName, i,"거래대금")
                date                = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "일자")
                market_value        = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                sTrCode, sRQName, i,"시가")
                high_value          = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                              sTrCode, sRQName, i, "고가")
                low_value           = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                             sTrCode, sRQName, i, "저가")

                data.append(current_price.strip())
                data.append(transaction_volume.strip())
                data.append(transaction_amount.strip())
                data.append(date.strip())
                data.append(market_value.strip())
                data.append(high_value.strip())
                data.append(low_value.strip())

                self.onedaypayListData.append(data.copy())

            print("현재 일봉 데이터량 %s" % len(self.onedaypayListData))
            #print("현재 데이터 리스트 %s" % self.onedaypayListData)

            if sPrevNext == "2":
                self.request_to_check_the_stock_pay_chart(eventCode = code, setsPrevNext=sPrevNext)
            else:

                print("총 일수 %s" % len(self.onedaypayListData))

                pass_success = None

                # 아직은 분석을 더해야됨 자세히 분석하지 못하였음
                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크해야됨 (120일 이평선을 보기위한 행위)
                if self.onedaypayListData == None or len(self.onedaypayListData) < 120:

                    pass_success = False

                # 120일 이상 일시
                else:
                    total_price = 0
                    # 리스트 슬라이싱
                    for value in self.onedaypayListData[:120]:

                        # 120일차에 1일현재가들을 전부 더한 값 total_price
                        total_price += int(value[0])

                        # 120일치 이평선 평균
                        average_horizontal = total_price/120

                        # 오늘자 주기기 120일 이평선에 걸쳐있는지 확인
                        bottom_stock_price = False
                        check_price = None

                        # 현재 봉(양봉,음봉 구별은 아직안함)이 평균이평선 안에 속해있을때
                        if int(self.onedaypayListData[0][6]) <= average_horizontal and average_horizontal <= int(self.onedaypayListData[0][5]):
                            print("오늘 주가 120이평선 확인")

                            # 이평선이 저가가 평균값보다 낮고 고가가 평균값보다 높아야합니다.
                            bottom_stock_price = True
                            price_top_move = False

                            # 현재 고가 가격
                            check_price = int(self.onedaypayListData[0][5])

                        # 과거 일봉들이 120일 이평선보다 밑에 있는지 확인
                        # 그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산 진행

                        if bottom_stock_price == True:

                            average_horizontal = 0

                            price_top_move = False

                            index = 1

                            while True:

                                # 120일치가 있는지 계속 확인
                                if len(self.onedaypayListData[index:]) < 120:
                                    print("120일치가 없음!")
                                    break

                                # 120일치 이평선이 있다는것이 확인된후 다시 구하기 위해 0 설정
                                total_price = 0

                                # 이해불능?
                                for value in self.onedaypayListData[index:120+index]:

                                    # 전날 120일차 이평선 현 시점 평균값을 구하기위한 전날 120일 총 현재가
                                    total_price += int(value[0])

                                # 전날 평균 이평선 값
                                move_average_horizontal = total_price / 120

                                # 전날 평균 이평선값이 전날 고가보다 낮고 이 상태로 20일보다 작아야 합니다.
                                if move_average_horizontal <= int(self.onedaypayListData[index][5]) and index <= 20:
                                    print("20일 동안 주기가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                    price_top_move = False
                                    break

                                # 전날 평균 이평선 값이 전날 저가보다 더 작고 20일차보다 커야됩니다.
                                elif int(self.onedaypayListData[index][6]) > move_average_horizontal and index > 20:
                                    print("120일 이평선 위에 있는 일봉 확인됨")
                                    price_top_move = True

                                    # 전날 저가 가격
                                    prev_price = int(self.onedaypayListData[index][6])
                                    break

                                else :
                                    index += 1

                            # 해당 부분 이평선이 가장 최근 일자의 이평선보다 가격이 낮은지 확인 하면서 현재 저가값이 전날 저가값보다
                            # 더 커야됩니다.
                            if price_top_move == True:
                                if average_horizontal > move_average_horizontal and check_price > prev_price:
                                    print("포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨")
                                    print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                    pass_success = True

                    if pass_success == True:
                        print("조건부 통과됨")

                        # 종목코드로 코드네임을 가져옵니다.
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                        # open이라는 파이썬 내장함수가 있습니다.
                        files_direction = open("files/condition_stock.txt", "a", encoding="utf8")

                        files_direction.write("%s\t%s\t%s\n" % (code, code_nm, str(self.onedaypayListData[0][0])))

                        files_direction.close()

                    elif pass_success == False:
                        print("조건부 통과 못함")

                    self.onedaypayListData.clear()
                    self.defult_account_info_event_loop.exit()

                self.defult_account_info_event_loop.exit()

    def read_code(self):

        if os.path.exists("S:/Python/Project_Yanajo/files/condition_stock.txt"): # 있으면 Ture 없으면 False

            # r = reading
            files_direction = open("S:/Python/Project_Yanajo/files/condition_stock.txt", "r", encoding="utf8")

            lines = files_direction.readlines()

            for line in lines:
                if line != "":
                    line_list = line.split("\t")

                    stock_code = line_list[0]
                    stock_name = line_list[1]
                    stock_price = int(line_list[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    # {"2027": {"종목명":"삼성 ....}....}]
                    self.files_stock_diet.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})

            # 메모리를 잡아먹지 않기위해 file을 닫아줍니다.
            files_direction.close()

            print(self.files_stock_diet)

    def screen_number_settings(self):

        # 겹치는 종목들을 알기위함
        screemOvering = []

        # 계좌잔고내역 종목 getter
        for getValueList in self.checkBalanceBox.keys():

            if getValueList not in screemOvering:

                # 0429(58-24:19)
                # 겹치는종목이 없다면은 해당 종목을 추가해줍니다.
                screemOvering.append(getValueList)

        # 미체결에 있는 종목들
        for getValueList in self.not_tighteningBox.keys():

            code = self.not_tighteningBox[getValueList]['종목코드']

            if code not in getValueList:
                screemOvering.append(code)

        # 리스트에 담겨있는 목록들
        for getValueList in self.files_stock_diet.keys():

            if getValueList not in screemOvering:

                screemOvering.append(getValueList)

        # 스크린번호 할당
        count = 0
        for getValueList in screemOvering:

            temp_screen = int(self.QscreenNumberFi)
            meme_screen = int(self.QscreenNumberS)

            # 100번째에 끊음
            if (count % 100) == 0:
                temp_screen += 1 #스크린 번호 하나당 데이터(종목코드) 100개를 넣어줌
                self.QscreenNumberFi = str(temp_screen)

                meme_screen += 1  # 스크린 번호 하나당 데이터(종목코드) 100개를 넣어줌
                self.QscreenNumberS = str(meme_screen)

            # 포함될때

            if getValueList in self.files_stock_diet.keys():

                # 각 종목들 한번에 모으기
                self.files_stock_diet[getValueList].update({"스크린번호" : self.QscreenNumberFi,
                                                            "주문용스크린번호" : self.QscreenNumberS})

            # 포함안될때
            elif getValueList not in self.files_stock_diet.keys():

                # 각 종목들 한번에 모으기
                self.files_stock_diet.update({getValueList : {"스크린번호" : self.QscreenNumberFi,
                                                            "주문용스크린번호" : self.QscreenNumberS}})

            count += 1
        print("files Array : %s" % self.files_stock_diet)

        """
        programer -> (삼성) -> 증권서버
        프로그래머가 삼성을 등록해놓음
        미리 이벤트랑 슬롯이랑 연결해놓은 구간이있습니다.
        그전에는 OnReceiveTrData를 통해서 슬롯과 연결했지만
        이번에는 OnReceiveRealData.connet(실시간수신슬롯)을 등록합니다.
        삼성이라는 데이터가 바뀌면은 바뀔때마다 서버에서 슬롯을 던져줍니다.
        여러가지를 불러오면서 files_stock_diet를 실시간 업데이트를 해줄겁니다.
        그리고 매수매도를 여기서 확인을 합니다.
        
        """

    # 0503 Testing Error
    def real_slot_call(self):

        self.dynamicCall("SetRealReg(QString, QString, QString, QString",
                         self.realTime_start_stop_QscreenNumberO, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")
        self.defult_account_info_event_loop.exec_()

    # 0503 Error : 실행안됨
    def realData_slot(self, sCode, sRealType, sRealData):
        """

        :param sCode: 종목코드
        :param sRealType: 실시간타입
        :param sRealData: 실시간 데이터 전문 (사용불능)
        :return: respons Data
        """

        print("RealTimeCode : %s" % sCode)
        print("RealTimeType : %s" % sRealType)
        print("RealTimeData : %s" % sRealData)

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            values = self.dynamicCall("GetCommRealData(QString, QString)", sCode, fid)

            # Test
            print(values)
            if values == 0:
                print('현재 시장이 닫은 시간이지만 시작 전 상태 입니다.')

            elif values == 3:
                print('현재 시장 운영중 입니다.')

            elif values == 2:
                print('현재 장 종료 10분 전 동시 호가입니다.')

            elif values == 4:
                print('현재 시장이 종료 되어 있습니다..')









