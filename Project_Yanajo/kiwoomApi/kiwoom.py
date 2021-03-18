from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
# QaxWidget 파이썬 파일중 컨테이너부분을 직접적으로 접근할수 있는 API로 서비스.서비스임플.맵퍼.DB (구현부안에 상속된건 아님) 추정됨
class Kiwoom(QAxWidget):

    """
    https://wikidocs.net/5755
    키움증권에서로 부터 설치한것은 OCX 방식에 컨포넌트 객체로 설치가 되었다.
    응용프로그램에서 키움Open API를 실행 할 수 있게 한거다.
    덕분에 제어가 된다.
    제어 할수 있는 함수는 PytQ5
    시그널 = 요청
    """

    def __init__(self):

        super().__init__() # 분모에있는 초기값들을 사용하기위해 분모에 있는 init을 사용한다.

        print("키움 API 연동")

        ############event_loop
        self.login_exec         = None
        ######################

        ############변수모음###
        self.account_BankNum    = None
        self.sPrevNext          = None
        self.checkBalanceBox    = {}
        self.not_tighteningBox  = {}
        #####################

        #############스크린 번호 모음
        self.QscreenNumberT      = 2000
        self.QscreenNumberF      = 4000

        ############유저 계좌 접근 변수
        self.userMoney          = None
        self.deposit_persent    = 0.5
        self.deposit_division   = 4
        ###########################

        #############이벤트 루프 모음
        self.defult_account_info_event_loop = QEventLoop()
        ###########################################

        self.get_Ocx_Install()
        self.event_List()

        self.signal_login_CommConnect()
        self.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
        self.get_account_info()

        # 예수금 조회
        self.deposit_acount_info()

        # 계좌평가잔고내역요청 조회
        self.checkBalance_acount_info()

    def get_Ocx_Install(self):

        """
        키움 API를 설치함으로써 응용프로그램들이 우리 window 레지스트리에 저장된다.
        레지스트리 편집기에 찾을수 있다.
        KHOPENAPI.KHOpenAPICtrl.1 폴더명으로 저장되며 DKHOPENAPI 기본값으로 설정되어있다.
        """

        # 응용프로그램을 제어하기 위한 그 설치된 경로를 지정해주어야됨
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_List(self):

        # 로그인용 이벤트 슬롯연결
        self.OnEventConnect.connect(self.login_slot)

        # TR용 이벤트 슬롯연결
        self.OnReceiveTrData.connect(self.trData_slot) # 여기가 문제인데???

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
                         '0', self.QscreenNumber)

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
                         setsPrevNext, self.QscreenNumber)

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
        print("주식일봉차트조회요청")

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", eventCode)
        self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", setsPrevNext)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회요청", "opt10081", setsPrevNext, self.QscreenNumberF)


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

        if (sRQName == "계좌평가잔고내역요청"):

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

        if (sRQName == "미체결요청"):

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

                print(self.not_tighteningBox)

            self.defult_account_info_event_loop.exit()



