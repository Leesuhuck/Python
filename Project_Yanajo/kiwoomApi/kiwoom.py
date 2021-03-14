from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
<<<<<<< Updated upstream
from method.errorCode import errors
=======
from config.errorCode import *
>>>>>>> Stashed changes
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
        self.login_exec = None
        ######################

        ############변수모음###
        self.account_BankNum = None
        #####################

<<<<<<< Updated upstream
        self.get_Ocx_Install()
=======
        #############이벤트 루프 모음
        self.defult_account_info_event_loop = None
        ###########################################
>>>>>>> Stashed changes

        self.get_Ocx_Install()
        self.event_List()

        self.signal_login_CommConnect()
        self.dynamicCall("KOA_Functions(String, String)", "ShowAccountWindow", "")
        self.get_account_info()

        # 예수금 조회
        self.deposit_acount_info()

        self.login_slot()

        self.get_account_info()

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

    # 로그인 버전처리 (계좌번호가져오기)
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCLIST")

        # split : 문자열 자르기 (계좌번호 가져올때 18545454545;45447878785; 이런식으로 출력됨)
        self.account_BankNum = account_list.split(';')[0]
        print('로그인 버전처리')

        # 현재 계좌번호
        print('현재 계좌 번호 %s' % self.account_BankNum)

    # 예수금 요청하는 부분
    def deposit_acount_info(self):
        print('예수금 조회 요청')

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_BankNum) # 계좌번호
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", '2') #2는 일반조회 3은 추정조회

        # 예수금 상세현황요청을 화면번호를 지정함
        self.dynamicCall("CommRqData(String, String, String, String)", "예수금상세현황요청", "opw00001", '0', "2000")
        print("예수금수행Test")

        # 다른데이터를 처리하는동안 다른작업을 할수있게 만드는것 이벤트 루프
        self.defult_account_info_event_loop = QEventLoop()
        self.defult_account_info_event_loop.exec_()

    def trData_slot(self, sScrNo, sRQName, sTrCode,sRecordName,sPrevNext):
        '''
        TR 요청을 받는 구역 (슬롯)
        :param sScrNo: 화면번호
        :param sRQName: 사용자 구분명
        :param sTrCode: TR이름
        :param sRecordName: 레코드이름
        :param sPrevNext: 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음 (다음페이지가 있는지)
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
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print(deposit)
            print("예수금 : %s" % deposit)
            print("예수금 형변환 : %s" % int(deposit))

            stock_evidence_cash = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "주식증거금현금")
            print("주식증거금현금 : %s" % stock_evidence_cash)
            print("주식증거금현금 형변환 : %s" % int(stock_evidence_cash))

            ture_deposit = self.dynamicCall("GetCommData(String, String, String, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 : %s" % ture_deposit)
            print("출금가능금액 형변환 : %d" % int(ture_deposit))

<<<<<<< Updated upstream
        self.login_exec.exec_() # 이벤트 루프 지정

    # 키움 에러처리 key
    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_exec.exec_()

    # 로그인 버전처리 (계좌번호가져오기)
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")
        account_list = self.dynamicCall("GetLoginInfo(String)", "USER_ID")

        # split : 문자열 자르기 (계좌번호 가져올때 18545454545;45447878785; 이런식으로 출력됨)
        account_BankNum = account_list.split(';')

        print('현재 계좌 번호 %s', account_BankNum)
=======
        self.defult_account_info_event_loop.exit()
>>>>>>> Stashed changes
