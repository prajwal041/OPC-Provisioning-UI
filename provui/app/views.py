
from django.shortcuts import render, render_to_response,redirect
from app.OracleComputeCloud import OracleComputeCloud
from django.views.decorators.csrf import csrf_exempt,csrf_protect,ensure_csrf_cookie
from django.contrib import messages
from app.models import Idd_data,Shapes,Document,Image,SSHkeys,Tier,Instance,Domain,Inventory
from app.forms import DocumentForm
import MySQLdb, xlrd,shutil,os
# Create your views here.

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

def logout(request):

    connection = MySQLdb.connect("localhost", "root", "Dev0p$123", "prov")
    cursord = connection.cursor()
    #cursord.execute("delete from account where user like %s",(request.session.get('username'),))
    cursord.execute("delete from image where user like %s",(request.session.get('username'),))
    cursord.execute("delete from sshkeys where user like %s",(request.session.get('username'),))
    cursord.execute("delete from shape where user like %s",(request.session.get('username'),))
    cursord.execute("delete from django_session")
    cursord.execute("delete from dom")
    cursord.execute("delete from app_document where user like %s", (request.session.get('username'),))

    user = request.session['username']
    documents = Document.objects.all()
    if documents:
        dir_name = '/tmp/documents/'
        basepath = os.path.join(dir_name, user)
        shutil.rmtree(basepath, ignore_errors=True)

    #request.session.flush()
    connection.commit()
    cursord.close()
    # try:
    #     del request.session['username']
    #
    #   #del request.session['password']
    # except:
    #     pass
    print request.session.get('username')
    return render_to_response('logout.html')

def cap_var(request):
    idds = request.POST.get('idd')  # Collecting the input values from the front end
    print idds
    if idds == None:                # checking IDD is None in the case of page refresh
        idds = "fonsi"              # Indicating IDD with NULL notation
    Domain.objects.create(dom=idds) # Loading IDD to the Domain table of Database

    if idds == "fonsi":             # whether IDD is NULL
        p = list(Domain.objects.values_list('dom').exclude(dom__contains="fonsi"))
        q = str(p).strip('[]')      # extract non-null values from database
        r = str(q).strip('()')
        s = r[:-1]                  # Data purification
        t = s[1:]
        u = t[:-1]
        idds = u[1:]
        print "database values"
        print idds

    #idd ='omcsops'
    p = list(Idd_data.objects.values_list('name').filter(name__contains=idds)) # Collecting authDomain from IDD
    q = str(p).strip('[]')
    r = str(q).strip('()')          # Data purification
    s = r[:-1]
    t = s[1:]
    u = t[:-1]
    authDomain = u[1:]
    print authDomain

    p = list(Idd_data.objects.values_list('api').filter(name__contains=authDomain)) # Collecting api from authDomain
    q = str(p).strip('[]')
    r = str(q).strip('()')          # Data purification
    s = r[:-1]
    t = s[1:]
    u = t[:-1]
    url = u[1:]
    print url

    p = list(Idd_data.objects.values_list('dccode').filter(name__contains=authDomain))  # Collecting dccode from authDomain
    q = str(p).strip('[]')
    r = str(q).strip('()')          # Data purification
    s = r[:-1]
    t = s[1:]
    u = t[:-1]
    dccode = u[1:]
    print dccode

    p = list(Idd_data.objects.values_list('custcode').filter(name__contains=authDomain))    # Collecting custcode from authDomain
    q = str(p).strip('[]')
    r = str(q).strip('()')          # Data purification
    s = r[:-1]
    t = s[1:]
    u = t[:-1]
    custcode = u[1:]
    print custcode

    account = '/Compute-%s' % (authDomain)  # account name from authDomain
    #account = Account.objects.values_list('name').filter(name__contains=acc)
    print account

    return (authDomain,url,dccode,custcode, account)

@ensure_csrf_cookie
@csrf_exempt
def ansviews(request, template_name='mypage.html'):
    """ Function for front end views of ansible UI webpage,
    Firstly it perform user authentication for valid users.
    Next it take the file input from user & validate the file content & Display it in the UI
    So that it can be used to submitted to build VM """

    if request.method == "POST" :   # checking POST request
        (authDomain, url, dccode, custcode, account) = cap_var(request)

        username = request.POST.get('username', '')     # get the input from front end text box
        password = request.POST.get('password', '')

        if request.session.get('username') == None: # checking username is NULL
            occ = OracleComputeCloud(endPointUrl=url, authenticationDomain=authDomain)
            cookies = occ.login(user=username, password=password) # Collecting the cookies from OCC Login

            if cookies == None or authDomain == None or url == None:    # checking either cookies, i/p is NULL
                return render_to_response('invalid.html') # redirect to invalid page
            else:
                tab2 = occ.getImageLists()          # Collecting the Image,SSH,Shape data from OCC(REST API)
                tab3 = occ.getSSHKeys()
                tab4 = occ.getShapes()

                request.session['username'] = username  # getting current User
                user = request.session['username']

                valimg = map(lambda x: (x['name']), tab2)   # Data purification through 'lamba' expression
                valssh = map(lambda x: (x['name']), tab3)
                valshape = map(lambda x: (x['name'],x['ram']), tab4)

                for name in valimg:             # loading data to the respective tables of the database
                    Image.objects.create(image_name=name, user=user)
                for name in valssh:
                    SSHkeys.objects.create(ssh_name=name, user=user)
                for name,ram in valshape:
                    Shapes.objects.create(shape_name=name, ram=ram, user=user)

        inventory = Inventory.objects.all()

        # uploading the input file
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():     # Form validation & save the content
            newdoc = Document(docfile=request.FILES['docfile'], user=request.session['username'])
            newdoc.save()
        documents = Document.objects.all()

        fauthDomain = []  # Global initialization of displayable values
        furl = []
        fdccode = []
        fcustcode = []
        faccount = []
        data = None
        length = []
        fshape = []
        fimage = []
        ftier = []
        finstance = []
        fsize = []
        size = '32'
        datavolsize = 0
        appinstance = None
        fdatavolsize = []
        fappinstance = []
        fssh = []
        backupvolsize = 0
        fbackupvolsize = []
        hostlabel = 'NULL'
        fhostlabel = []
        seclist = 'NULL'
        fseclist = []
        fpagevolsize = []
        pagevolsize = 'NULL'
        femvolsize = []
        emvolsize = 'NULL'
        fdatacenter = []
        datacenter = 'NULL'
        shapeflag = 0
        datavolflag = 0
        appinstanceflag = 0
        tierflag = 0
        instanceflag = 0
        imageflag = 0
        sshflag = 0
        fstatus = []
        fdbstatus = []

        if not documents:       # whether the document is empty ....!!
            print "Empty doc"
        else:                   # Executing the content of the document
            print "Boda sheera...!!"
            #file = "C:\Users\prajshet\Desktop\Infra_atmn\BMCS\machines.xlsx"
            request.session['username'] = username  # getting current User
            user = request.session['username']
            path = ''
            basepath = '/tmp/documents'
            for fname in os.listdir(basepath):
                path = os.path.join(basepath, fname)
            li = os.listdir(path)
            workbook = xlrd.open_workbook(path + "/" + li[0])     # getting the data of the .xlsx file
            sheet = workbook.sheet_by_index(0)
            row = range(sheet.nrows)                # Read from 1st row & discard header row
            data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in row[1:]]

            for i in range(len(data)):
                shape = Shapes.objects.values('shape_name') # Getting all shape_name from database
                list_shape = [entry for entry in shape]
                valshape = map(lambda x: (x['shape_name']), list_shape) # Data purification
                if data[i][0] in valshape:              # validating shape
                    fshape.append(data[i][0])           # append the data to list
                    fauthDomain.append(authDomain)      # append domain,url,dccode,custcode,account
                    furl.append(url)
                    fdccode.append(dccode)
                    fcustcode.append(custcode)
                    faccount.append(account)
                    shapeflag =1                        # setting shape flag

                datavolsize = data[i][1]
                if isinstance(datavolsize, float) == True:  # validating datavolsize
                    fdatavolsize.append(data[i][1])         # append the data to list
                    datavolflag = 1                     # setting datavolflag
                    print "Valid DataVolume"

                appinstance = data[i][2]                # validating appinstance
                if isinstance(appinstance, unicode) == True and shapeflag == 1 and datavolflag == 1:
                    fappinstance.append(data[i][2])     # append the data to list
                    appinstanceflag = 1                 # setting appinstanceflag
                    print "Valid AppInstance"

                tier = Tier.objects.values('tier_name') # Getting all tier_name from database
                list_tier = [entry for entry in tier]
                valtier = map(lambda x: (x['tier_name']), list_tier)    # data purification
                if data[i][3] in valtier:               # validating tier
                    ftier.append(data[i][3])            # append the data to list
                    tierflag = 1                        # setting tierflag

                instance = Instance.objects.values('inst_name') # Getting all instance_name from database
                list_instance = [entry for entry in instance]
                valinstance = map(lambda x: (x['inst_name']), list_instance)    # data purification
                if data[i][4] in valinstance:           # validating tier
                    finstance.append(data[i][4])        # append the data to list
                    instanceflag = 1                    # setting instanceflag

                image = Image.objects.values('image_name')  # Getting all image_name from database
                list_image = [entry for entry in image]
                valimage = map(lambda x: (x['image_name']), list_image) # data purification
                if data[i][6] in valimage:              # validating tier
                    fimage.append(data[i][6])           # append the data to list
                    imageflag = 1                       # setting imageflag
                    if "Microsoft" in fimage[-1]:       # whether the image is of the type "Microsoft"....!!
                        p = list(Shapes.objects.values_list('ram').filter(shape_name=fshape[-1]))
                        q = str(p).strip('[]')          # Getting all ram size matching shape from database
                        r = str(q).strip('()')
                        s = r[:-1]
                        t = s[1:]
                        u = t[:-1]
                        rams = u[1:]
                        ramint = int(rams)
                        ram = ramint / 1024  # calculating ram
                        pagevolsize = (ram * 1.5) + 1  # calculating pagevolumesize
                        fpagevolsize.append(pagevolsize)  # appending pagevolumesize to the list
                        emvolsize = 10  # static emvolsize
                        femvolsize.append(emvolsize)  # appending emvolumesize to the list
                        datacenter = url[24:27]  # datacenter for Microfoft image
                        fdatacenter.append(datacenter)  # appending emvolumesize to the list
                        size = '64'  # OS Size for Microsoft image
                        fsize.append(size)  # appending size to the list
                        sizeno = int(size)
                        datavol = int(datavolsize)  # Calculating footprint
                        footprint = sizeno + datavol
                        backupvolsize = footprint * 1.5  # Calculating backupvolumesize
                        fbackupvolsize.append(backupvolsize)  # appending backupvolumesize to the list
                        region = url[24:27].upper()  # Derived Region from API
                        zone = url[12:15].upper()  # Derived Zone from API
                        hostlabel = '%s-%s-%s-%s001' % (
                        region, zone, appinstance, finstance[-1])  # Calculating hostlabel
                        fhostlabel.append(hostlabel)  # appending hostlabel to the list
                        seclist = 'SL-%s-%s-%s-001' % (custcode, ftier[-1], finstance[-1])  # Calculating seclist
                        fseclist.append(seclist)  # appending seclist to the list
                    else:
                        pagevolsize = None  # Pagevolume is 'None for Linux image
                        fpagevolsize.append(pagevolsize)  # appending pagecolumesize to the list
                        emvolsize = None  # emvolume is 'None for Linux image
                        femvolsize.append(emvolsize)  # appending emcolumesize to the list
                        datacenter = None  # datacenter is 'None for Linux image
                        fdatacenter.append(datacenter)  # appending datacenter to the list
                        size = '32'  # OS Size for Linux image
                        fsize.append(size)  # appending size to the list
                        sizeno = int(size)
                        datavol = int(datavolsize)
                        footprint = sizeno + datavol  # Calculating footprint
                        backupvolsize = footprint * 1.5  # Calculating backupvolumesize
                        fbackupvolsize.append(backupvolsize)  # appending backupvolumesize to the list
                        region = url[24:27].upper()  # Derived Region from API
                        zone = url[12:15].upper()  # Derived Zone from API
                        hostlabel = '%s-%s-%s-%s001' % (
                        region, zone, appinstance, finstance[-1])  # Calculating hostlabel
                        fhostlabel.append(hostlabel)  # appending hostlabel to the list
                        seclist = 'SL-%s-%s-%s-001' % (custcode, ftier[-1], finstance[-1])  # Calculating seclist
                        fseclist.append(seclist)  # appending seclist to the list

                ssh = SSHkeys.objects.values('ssh_name')    # Getting all ssh_name from database
                list_ssh = [entry for entry in ssh]
                valssh = map(lambda x: (x['ssh_name']), list_ssh)   # data purification
                if data[i][5] in valssh:                    # validating ssh
                    fssh.append(data[i][5])                 # append the data to list
                    sshflag = 1                             # setting sshflag

                if shapeflag == 1 and datavolflag == 1 and appinstanceflag == 1 and tierflag == 1 and instanceflag == 1 and imageflag == 1 and sshflag == 1:
                    status = 'VALID'  # Validating status from all flags
                    shapeflag = 0
                    datavolflag = 0
                    appinstanceflag = 0  # Resetting the flags
                    tierflag = 0
                    instanceflag = 0
                    imageflag = 0
                    sshflag = 0
                    if (Inventory.objects.filter(hostlabel__contains=hostlabel, authDomain__contains=authDomain)):
                        messages.info(request, "Entry exists in Inventory")
                        db_status = 'EXISTS'
                        pass
                    else:
                        Inventory.objects.create(authDomain=authDomain, url=url, dccode=dccode, custcode=custcode,
                                                 account=account, size=size, shape=data[i][0], image=data[i][6],
                                                 datavolsize=data[i][1], appinstance=data[i][2],
                                                 backupvolsize=backupvolsize, hostlabel=hostlabel, seclist=seclist,
                                                 tier=data[i][3], instance=data[i][4], ssh=data[i][5],
                                                 pagevolsize=pagevolsize, emvolsize=emvolsize, datacenter=datacenter,
                                                 user=user)
                        db_status = 'PUSHED'
                        print "Inventory Loading Success..!!"
                else:
                    status = 'INVALID'
                    db_status = 'IGNORED'

                fstatus.append(status)              # Appending status to the list
                fdbstatus.append(db_status)  # Appending inventory status to the list

        # Zipping the data for template
        zipped_data = zip(fauthDomain,furl,fdccode,fcustcode,faccount,fsize,fshape,fimage,fdatavolsize,fappinstance,fbackupvolsize,fhostlabel,fseclist,ftier,finstance,fssh,fpagevolsize,femvolsize,fdatacenter)
        context = {
            'zipped_data': zipped_data,
            'data': data,
            'inventory': inventory,
            'fstatus': fstatus,
            'fdbstatus': fdbstatus,
            'length': length,
            'fauthDomain': fauthDomain,
            'furl': furl,
            'documents': documents,
            'fdccode': fdccode,
            'fcustcode': fcustcode,
            'fsize': fsize,
            'faccount': faccount,
            'form': form,
            'fshape': fshape,
            'fimage': fimage,
            'ftier': ftier,
            'finstance': finstance,
            'datavolsize': datavolsize,
            'appinstance': appinstance,
            'fdatavolsize': fdatavolsize,
            'fappinstance': fappinstance,
            'fbackupvolsize': fbackupvolsize,
            'fhostlabel': fhostlabel,
            'fseclist': fseclist,
            'fssh': fssh,
            'fpagevolsize': fpagevolsize,
            'femvolsize': femvolsize,
            'fdatacenter': fdatacenter,
        }
        return render(request, template_name, context)                   #return the page requestfor the template page
    else:
        print "GET Type"

        form = DocumentForm()  # A empty, unbound form

        # Load documents for the list page
        documents = Document.objects.all()

        connection = MySQLdb.connect("localhost", "root", "Dev0p$123", "prov")
        cursord = connection.cursor()
        cursord.execute('''select idd from idd_data GROUP BY idd''')
        Domain = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select customer from idd_data GROUP BY customer''')
        customer = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select zone from idd_data GROUP BY zone''')
        zone = dictfetchall(cursord)

        #template_name = 'mypage.html'

        context = {
            'Domain': Domain,
            'customer': customer,
            'zone': zone,
            'documents': documents,
            'form': form,
        }
        return render(request, template_name,context)

def validviews(request, template_name='valid.html'):            # Function for valid data(2nd page)
    if request.method == 'POST':
        (authDomain, url, dccode, custcode, account) = cap_var(request)
        print "2nd page disp"
        shape  = request.POST.get('shape_name', '')
        image = request.POST.get('image_name', '')
        datavolsize = request.POST.get('datavol', '')
        appinstance = request.POST.get('ainstance', '')
        tier = request.POST.get('tier_name', '')
        instance = request.POST.get('inst_name', '')
        sshkeys = request.POST.get('ssh_name','')
        size = '32'
        pagevolsize = None
        emvolsize = None
        datacenter = None
        if "Microsoft" in image:
            p = list(Shapes.objects.values_list('ram').filter(shape_name=shape))
            q = str(p).strip('[]')
            r = str(q).strip('()')
            s = r[:-1]
            t = s[1:]
            u = t[:-1]
            rams = u[1:]
            ramint = int(rams)
            ram = ramint / 1024
            pagevolsize = (ram * 1.5) + 1
            emvolsize = 10
            datacenter = url[24:27]
            size = '64'


        connection = MySQLdb.connect("localhost", "root", "Dev0p$123", "prov")
        cursord = connection.cursor()
        cursord.execute('''select shape_name from shape where shape_name="%s"''' % (shape))
        shape_name = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select size_name from size where size_name="%s"''' %(size))
        size_name = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select image_name from image where image_name="%s"''' % (image))
        image_name = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select tier_name from tier where tier_name="%s"''' % (tier))
        tier_name = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select inst_name from instance where inst_name="%s"''' % (instance))
        inst_name = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select ssh_name from sshkeys where ssh_name="%s"''' % (sshkeys))
        ssh_name = dictfetchall(cursord)

        sizeno = int(size)
        data = int(datavolsize)
        footprint = sizeno + data
        backupvolsize = footprint * 1.5
        hostlabel = '%s-%s-01' %(appinstance,instance)
        seclist = 'SL-%s-%s-%s-001' %(custcode,tier,instance)

        cursord = connection.cursor()
        cursord.execute('''select image_name from image GROUP BY image_name''')
        image = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select shape_name from shape GROUP BY shape_name''')
        shape = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select size_name from size GROUP BY size_name''')
        size = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select tier_name from tier GROUP BY tier_name''')
        tier = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select inst_name from instance GROUP BY inst_name''')
        instance = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select ssh_name from sshkeys GROUP BY ssh_name''')
        sshkeys = dictfetchall(cursord)

        context = {
            'authDomain': authDomain,
            'url': url,
            'dccode': dccode,
            'image': image,
            'shape': shape,
            'size': size,
            'custcode': custcode,
            'datavolsize': datavolsize,
            'appinstance': appinstance,
            'tier': tier,
            'instance': instance,
            'backupvolsize': backupvolsize,
            'hostlabel': hostlabel,
            'seclist': seclist,
            'sshkeys': sshkeys,
            'image_name': image_name,
            'shape_name': shape_name,
            'size_name': size_name,
            'tier_name': tier_name,
            'inst_name': inst_name,
            'ssh_name': ssh_name,
            'account': account,
            'pagevolsize': pagevolsize,
            'emvolsize': emvolsize,
            'datacenter': datacenter,
        }
        return render(request, template_name,context)
    else:
        print "valid GET type"
        connection = MySQLdb.connect("localhost", "root", "Dev0p$123", "prov")

        cursord = connection.cursor()
        cursord.execute('''select image_name from image GROUP BY image_name''')
        image = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select shape_name from shape GROUP BY shape_name''')
        shape = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select size_name from size GROUP BY size_name''')
        size = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select tier_name from tier GROUP BY tier_name''')
        tier = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select inst_name from instance GROUP BY inst_name''')
        instance = dictfetchall(cursord)

        cursord = connection.cursor()
        cursord.execute('''select ssh_name from sshkeys GROUP BY ssh_name''')
        sshkeys = dictfetchall(cursord)

        context = {
            'image': image,
            'shape' : shape,
            'size': size,
            'tier': tier,
            'instance': instance,
            'sshkeys': sshkeys,
        }
        return render(request, template_name,context)

def help(request, template_name='help.html'):

    return render(request, template_name)

