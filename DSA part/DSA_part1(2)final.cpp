#include <iostream>
#include <fstream>
#include <string>
#include <queue>
#include <stack>
#include <sstream>
#include <limits>
#include <cstdlib>
#include <vector>
#include <algorithm>

using namespace std;

// ==================== UTILITY FUNCTIONS ====================

string EscapeCSV(const string& field)
{
    string result = field;
    bool needsQuotes = false;
    
    // Check for special characters
    if (field.find(',') != string::npos || 
        field.find('"') != string::npos || 
        field.find('\n') != string::npos) 
        {
            needsQuotes = true;
        }
    
    // Escape quotes by doubling them
    size_t pos = 0;
    while ((pos = result.find('"', pos)) != string::npos) 
    {
        result.insert(pos, "\"");
        pos += 2;
    }
    
    if (needsQuotes) 
    {
        result = "\"" + result + "\"";
    }
    
    return result;
}

string UnescapeCSV(const string& field)
{
    string result = field;
    if (!result.empty() && result.front() == '"' && result.back() == '"')
    {
        result = result.substr(1, result.length() - 2);
    }
    return result;
}

int GetValidInteger()
{
    int value;
    while (!(cin >> value))
    {
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        cout << "Invalid input! Please enter a valid number: ";
    }
    return value;
}

double GetValidDouble()
{
    double value;
    while (!(cin >> value) || value < 0)
    {
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        cout << "Invalid input! Please enter a valid amount: ";
    }
    return value;
}

//-------------------------------Creating AI integration file-----------------------------------------------

void CreateAIInputFile(const string& symptoms)
{
    // Load all symptoms from dataset-based file
    ifstream symptomFile("../symptoms.txt");
    if (!symptomFile.is_open())
    {
        cout << "Error: symptoms.txt file not found.\n";
        return;
    }

    vector<string> allSymptoms;
    string symptom;

    while (getline(symptomFile, symptom))
    {
        if (!symptom.empty())
            allSymptoms.push_back(symptom);
    }
    symptomFile.close();

    ofstream file("../ai_input.csv");
    if (!file.is_open())
    {
        cout << "Could not create AI input file.\n";
        return;
    }

    // Write header (must match dataset order)
    for (const string& s : allSymptoms)
        file << s << ",";
    file << "prognosis\n";

    // Normalize input symptoms
    string input = symptoms;
    transform(input.begin(), input.end(), input.begin(), ::tolower);

    // Write feature row
    for (const string& s : allSymptoms)
    {
        if (input.find(s) != string::npos)
            file << "1,";
        else
            file << "0,";
    }

    file << "?\n";
    file.close();

    cout << "AI input file generated using full dataset symptoms.\n";
}

// ==================== PATIENT MANAGEMENT MODULE ====================

struct Patientrecord
{
    int patientid;
    string fullname;
    int age;
    string gender;
    string phonenumber;
    string medicalhistory;
    string currentsymptoms;
    Patientrecord* nextpatient;

    Patientrecord()
    {
        patientid = 0;
        age = 0;
        nextpatient = NULL;
    }
};

class Patientmanager
{
private:
    Patientrecord* headpatient;
    int nextpatientid;

    void Loadpatientsfromfile()
    {
        ifstream inputfile("patients.csv");
        if (!inputfile.is_open())
        {
            return;
        }

        string currentline;
        getline(inputfile, currentline); // skip header

        while (getline(inputfile, currentline))
        {
            if (currentline.empty())
            {
                continue;
            }

            stringstream linestream(currentline);
            string idstr, name, agestr, gender, phone, history, symptoms;

            getline(linestream, idstr, ',');
            getline(linestream, name, ',');
            getline(linestream, agestr, ',');
            getline(linestream, gender, ',');
            getline(linestream, phone, ',');
            getline(linestream, history, ',');
            getline(linestream, symptoms, ',');

            Patientrecord* newpatient = new Patientrecord();
            newpatient->patientid = atoi(idstr.c_str());
            newpatient->fullname = name;
            newpatient->age = atoi(agestr.c_str());
            newpatient->gender = gender;
            newpatient->phonenumber = phone;
            newpatient->medicalhistory = history;
            newpatient->currentsymptoms = symptoms;
            newpatient->nextpatient = NULL;

            if (!headpatient)
            {
                headpatient = newpatient;
            }
            else
            {
                Patientrecord* current = headpatient;
                while (current->nextpatient)
                {
                    current = current->nextpatient;
                }
                current->nextpatient = newpatient;
            }

            if (newpatient->patientid >= nextpatientid)
            {
                nextpatientid = newpatient->patientid + 1;
            }
        }

        inputfile.close();
    }

    void Savepatientstofile()
    {
        ofstream outputfile("patients.csv");
        outputfile << "ID,Name,Age,Gender,Contact,MedicalHistory,Symptoms\n";

        Patientrecord* current = headpatient;
        while (current)
        {
            outputfile << current->patientid << ","
                        << EscapeCSV(current->fullname) << ","
                        << current->age << ","
                        << EscapeCSV(current->gender) << ","
                        << EscapeCSV(current->phonenumber) << ","
                        << EscapeCSV(current->medicalhistory) << ","
                        << EscapeCSV(current->currentsymptoms) << "\n";

            current = current->nextpatient;
        }

        outputfile.close();
    }

public:
    Patientmanager()
    {
        headpatient = NULL;
        nextpatientid = 1;
        Loadpatientsfromfile();
    }

    void Addnewpatient()
    {
        Patientrecord* newpatient = new Patientrecord();
        newpatient->patientid = nextpatientid++;

        cout << "\nEnter Full Name: ";
        cin.ignore();
        getline(cin, newpatient->fullname);

        cout << "Enter Age: ";
        cin >> newpatient->age;

        cout << "Enter Gender: ";
        cin >> newpatient->gender;

        cout << "Enter Contact Number: ";
        cin >> newpatient->phonenumber;

        cout << "Enter Medical History: ";
        cin.ignore();
        getline(cin, newpatient->medicalhistory);

        cout << "Enter Current Symptoms: ";
        getline(cin, newpatient->currentsymptoms);

        newpatient->nextpatient = NULL;

        if (!headpatient)
        {
            headpatient = newpatient;
        }
        else
        {
            Patientrecord* current = headpatient;
            while (current->nextpatient)
            {
                current = current->nextpatient;
            }
            current->nextpatient = newpatient;
        }

        Savepatientstofile();
        CreateAIInputFile(newpatient->currentsymptoms);
        cout << "\nPatient registered successfully! Assigned ID: "
             << newpatient->patientid << endl;
    }

    Patientrecord* Findpatientbyid(int searchid)
    {
        Patientrecord* current = headpatient;
        while (current)
        {
            if (current->patientid == searchid)
            {
                return current;
            }
            current = current->nextpatient;
        }
        return NULL;
    }

    void Updatepatientinfo()
    {
        int searchid;
        cout << "Enter Patient ID to Update: ";
        cin >> searchid;

        Patientrecord* patient = Findpatientbyid(searchid);
        if (!patient)
        {
            cout << "Patient not found!\n";
            return;
        }

        cout << "New Name: ";
        cin.ignore();
        getline(cin, patient->fullname);

        cout << "New Age: ";
        cin >> patient->age;

        cout << "New Contact: ";
        cin >> patient->phonenumber;

        Savepatientstofile();
        cout << "Patient information updated successfully!\n";
    }

    void Removepatient()
    {
        int removeid;
        cout << "Enter Patient ID to Remove: ";
        cin >> removeid;

        if (!headpatient)
        {
            cout << "No patients available!\n";
            return;
        }

        if (headpatient->patientid == removeid)
        {
            Patientrecord* temp = headpatient;
            headpatient = headpatient->nextpatient;
            Savepatientstofile();
            delete temp;
            cout << "Patient removed successfully!\n";
            return;
        }

        Patientrecord* current = headpatient;
        while (current->nextpatient && current->nextpatient->patientid != removeid)
        {
            current = current->nextpatient;
        }

        if (current->nextpatient)
        {
            Patientrecord* temp = current->nextpatient;
            current->nextpatient = temp->nextpatient;
            Savepatientstofile();
            delete temp;
            cout << "Patient removed successfully!\n";
        }
        else
        {
            cout << "Patient not found!\n";
        }
    }

    void Displayallpatients()
    {
        if (!headpatient)
        {
            cout << "No patients registered.\n";
            return;
        }

        cout << "\n========== ALL PATIENTS ==========\n";
        Patientrecord* current = headpatient;
        while (current)
        {
            cout << "ID: " << current->patientid
                 << " | Name: " << current->fullname
                 << " | Age: " << current->age
                 << " | Contact: " << current->phonenumber << endl;

            current = current->nextpatient;
        }
    }
    ~Patientmanager() 
    {
        Patientrecord* current = headpatient;
        while (current) 
        {
            Patientrecord* temp = current;
            current = current->nextpatient;
            delete temp;
        }
    }
};

// ==================== DOCTOR MANAGEMENT MODULE ====================

struct Doctorrecord
{
    int doctorid;
    string fullname;
    string specialization;
    int yearsofexperience;
    string contactnumber;
    string availableslots;
    Doctorrecord* nextdoctor;

    Doctorrecord()
    {
        doctorid = 0;
        yearsofexperience = 0;
        nextdoctor = NULL;
    }
};

class Doctormanager
{
private:
    Doctorrecord* headdoctor;
    int nextdoctorid;

    void Loaddoctorsfromfile()
    {
        ifstream inputfile("doctors.csv");
        if (!inputfile.is_open())
        {
            return;
        }

        string currentline;
        getline(inputfile, currentline); // skip header

        while (getline(inputfile, currentline))
        {
            if (currentline.empty())
            {
                continue;
            }

            stringstream linestream(currentline);
            string idstr, name, spec, expstr, contact, availability;

            getline(linestream, idstr, ',');
            getline(linestream, name, ',');
            getline(linestream, spec, ',');
            getline(linestream, expstr, ',');
            getline(linestream, contact, ',');
            getline(linestream, availability, ',');

            Doctorrecord* newdoctor = new Doctorrecord();
            newdoctor->doctorid = atoi(idstr.c_str());
            newdoctor->fullname = name;
            newdoctor->specialization = spec;
            newdoctor->yearsofexperience = atoi(expstr.c_str());
            newdoctor->contactnumber = contact;
            newdoctor->availableslots = availability;
            newdoctor->nextdoctor = NULL;

            if (!headdoctor)
            {
                headdoctor = newdoctor;
            }
            else
            {
                Doctorrecord* current = headdoctor;
                while (current->nextdoctor)
                {
                    current = current->nextdoctor;
                }
                current->nextdoctor = newdoctor;
            }

            if (newdoctor->doctorid >= nextdoctorid)
            {
                nextdoctorid = newdoctor->doctorid + 1;
            }
        }

        inputfile.close();
    }

    void Savedoctorstofile()
    {
        ofstream outputfile("doctors.csv");
        outputfile << "ID,Name,Specialization,Experience,Contact,Availability\n";

        Doctorrecord* current = headdoctor;
        while (current)
        {
            outputfile << current->doctorid << ","
                        << EscapeCSV(current->fullname) << ","
                        << EscapeCSV(current->specialization) << ","
                        << current->yearsofexperience << ","
                        << EscapeCSV(current->contactnumber) << ","
                        << EscapeCSV(current->availableslots) << "\n";

            current = current->nextdoctor;
        }

        outputfile.close();
    }

public:
    Doctormanager()
    {
        headdoctor = NULL;
        nextdoctorid = 1;
        Loaddoctorsfromfile();
    }

    void Addnewdoctor()
    {
        Doctorrecord* newdoctor = new Doctorrecord();
        newdoctor->doctorid = nextdoctorid++;

        cout << "\nEnter Full Name: ";
        cin.ignore();
        getline(cin, newdoctor->fullname);

        cout << "Enter Specialization: ";
        getline(cin, newdoctor->specialization);

        cout << "Enter Years of Experience: ";
        cin >> newdoctor->yearsofexperience;

        cout << "Enter Contact Number: ";
        cin >> newdoctor->contactnumber;

        cout << "Enter Available Time Slots: ";
        cin.ignore();
        getline(cin, newdoctor->availableslots);

        newdoctor->nextdoctor = NULL;

        if (!headdoctor)
        {
            headdoctor = newdoctor;
        }
        else
        {
            Doctorrecord* current = headdoctor;
            while (current->nextdoctor)
            {
                current = current->nextdoctor;
            }
            current->nextdoctor = newdoctor;
        }

        Savedoctorstofile();
        cout << "\nDoctor registered successfully! Assigned ID: "
             << newdoctor->doctorid << endl;
    }

    Doctorrecord* Finddoctorbyid(int searchid)
    {
        Doctorrecord* current = headdoctor;
        while (current)
        {
            if (current->doctorid == searchid)
            {
                return current;
            }
            current = current->nextdoctor;
        }
        return NULL;
    }

    void Searchbyspecialization()
    {
        string searchspec;
        cout << "Enter Specialization to Search: ";
        cin.ignore();
        getline(cin, searchspec);

        bool found = false;
        Doctorrecord* current = headdoctor;

        cout << "\n========== DOCTORS (" << searchspec << ") ==========\n";
        while (current)
        {
            if (current->specialization == searchspec)
            {
                cout << "ID: " << current->doctorid
                     << " | Name: " << current->fullname
                     << " | Experience: "
                     << current->yearsofexperience << " years\n";
                found = true;
            }
            current = current->nextdoctor;
        }

        if (!found)
        {
            cout << "No doctors found with this specialization.\n";
        }

    }

    void Displayalldoctors()
    {
        if (!headdoctor)
        {
            cout << "No doctors registered.\n";
            return;
        }

        cout << "\n========== ALL DOCTORS ==========\n";
        Doctorrecord* current = headdoctor;
        while (current)
        {
            cout << "ID: " << current->doctorid
                 << " | Name: " << current->fullname
                 << " | Specialization: "
                 << current->specialization << endl;

            current = current->nextdoctor;
        }
    }
    ~Doctormanager()
    {
        Doctorrecord* current = headdoctor;
        while (current) 
        {
            Doctorrecord* temp = current;
            current = current->nextdoctor;
            delete temp;
        }
    }
};

// ==================== STAFF MANAGEMENT MODULE ====================

// ==================== STAFF MANAGEMENT MODULE ====================

struct Staffmember
{
    int staffid;
    string fullname;
    string workshift;
    string department;
    Staffmember* nextstaff;

    Staffmember()
    {
        staffid = 0;
        nextstaff = NULL;
    }
};

class Staffmanager
{
private:
    Staffmember* headstaff;
    queue<Staffmember*> dutyrotationqueue;
    int nextstaffid;

    void Loadstafffromfile()
    {
        ifstream inputfile("staff.csv");
        if (!inputfile.is_open())
        {
            return;
        }

        string line;
        getline(inputfile, line); // skip header

        while (getline(inputfile, line))
        {
            if (line.empty()) continue;

            stringstream ss(line);
            string id, name, shift, dept;

            getline(ss, id, ',');
            getline(ss, name, ',');
            getline(ss, shift, ',');
            getline(ss, dept, ',');

            Staffmember* staff = new Staffmember();
            staff->staffid = atoi(id.c_str());
            staff->fullname = UnescapeCSV(name);
            staff->workshift = UnescapeCSV(shift);
            staff->department = UnescapeCSV(dept);
            staff->nextstaff = NULL;

            if (!headstaff)
            {
                headstaff = staff;
            }
            else
            {
                Staffmember* temp = headstaff;
                while (temp->nextstaff)
                {
                    temp = temp->nextstaff;
                }
                temp->nextstaff = staff;
            }

            dutyrotationqueue.push(staff);

            if (staff->staffid >= nextstaffid)
            {
                nextstaffid = staff->staffid + 1;
            }
        }

        inputfile.close();
    }

    void Savestafftofile()
    {
        ofstream outputfile("staff.csv");
        outputfile << "ID,Name,Shift,Department\n";

        Staffmember* current = headstaff;
        while (current)
        {
            outputfile << current->staffid << ","
                       << EscapeCSV(current->fullname) << ","
                       << EscapeCSV(current->workshift) << ","
                       << EscapeCSV(current->department) << "\n";

            current = current->nextstaff;
        }

        outputfile.close();
    }

public:
    Staffmanager()
    {
        headstaff = NULL;
        nextstaffid = 1;
        Loadstafffromfile();
    }

    void Addnewstaffmember()
    {
        Staffmember* newstaff = new Staffmember();
        newstaff->staffid = nextstaffid++;

        cout << "\nEnter Full Name: ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, newstaff->fullname);

        cout << "Enter Shift (Morning/Evening/Night): ";
        getline(cin, newstaff->workshift);

        cout << "Enter Department: ";
        getline(cin, newstaff->department);

        newstaff->nextstaff = NULL;

        if (!headstaff)
        {
            headstaff = newstaff;
        }
        else
        {
            Staffmember* current = headstaff;
            while (current->nextstaff)
            {
                current = current->nextstaff;
            }
            current->nextstaff = newstaff;
        }

        dutyrotationqueue.push(newstaff);
        Savestafftofile();

        cout << "\nStaff member registered successfully! Assigned ID: "
             << newstaff->staffid << endl;
    }

    void Assignnextduty()
    {
        if (dutyrotationqueue.empty())
        {
            cout << "No staff available for duty rotation!\n";
            return;
        }

        Staffmember* assignedstaff = dutyrotationqueue.front();
        dutyrotationqueue.pop();

        cout << "Assigned to duty: "
             << assignedstaff->fullname
             << " (ID: " << assignedstaff->staffid << ")"
             << " - Department: "
             << assignedstaff->department << endl;

        dutyrotationqueue.push(assignedstaff);
    }

    void Displaydutyroster()
    {
        if (dutyrotationqueue.empty())
        {
            cout << "Duty roster is empty!\n";
            return;
        }

        cout << "\n========== DUTY ROSTER ==========\n";
        queue<Staffmember*> tempqueue = dutyrotationqueue;
        int position = 1;

        while (!tempqueue.empty())
        {
            Staffmember* staff = tempqueue.front();
            cout << position++ << ". "
                 << staff->fullname << " - "
                 << staff->department << " ("
                 << staff->workshift << " Shift)"
                 << endl;

            tempqueue.pop();
        }
    }

    ~Staffmanager()
    {
        Staffmember* current = headstaff;
        while (current)
        {
            Staffmember* temp = current;
            current = current->nextstaff;
            delete temp;
        }
    }
};

// ==================== BILLING SYSTEM MODULE ====================

struct Billingitem
{
    string itemdescription;
    double itemcost;

    Billingitem()
    {
        itemcost = 0.0;
    }
};

class Billingsystem
{
private:
    stack<Billingitem> billingstack;

public:
    void Addservicecharge()
    {
        Billingitem newitem;

        cout << "\n=== Add Service Charge ===\n";
        cout << "Enter Service Description: ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, newitem.itemdescription);

        cout << "Enter Amount ($): ";
        newitem.itemcost = GetValidDouble();

        billingstack.push(newitem);
        cout << "Service charge added to bill!\n";
    }

    void Addmedicinecharge()
    {
        Billingitem newitem;

        cout << "\n=== Add Medicine Charge ===\n";
        cout << "Enter Medicine Name: ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, newitem.itemdescription);

        cout << "Enter Amount ($): ";
        newitem.itemcost = GetValidDouble();

        billingstack.push(newitem);
        cout << "Medicine charge added to bill!\n";
    }

    void Removelastitem()
    {
        if (billingstack.empty())
        {
            cout << "No items in bill to remove!\n";
            return;
        }

        cout << "Removed item: "
             << billingstack.top().itemdescription
             << " ($" << billingstack.top().itemcost << ")\n";

        billingstack.pop();
    }

    void Generatefinalbill()
    {
        if (billingstack.empty())
        {
            cout << "No items in the bill!\n";
            return;
        }

        double totalamount = 0.0;
        stack<Billingitem> tempstack = billingstack;

        cout << "\n============================================\n";
        cout << "          HOSPITAL BILL STATEMENT            \n";
        cout << "============================================\n";

        while (!tempstack.empty())
        {
            cout << tempstack.top().itemdescription
                 << " : $" << tempstack.top().itemcost << endl;

            totalamount += tempstack.top().itemcost;
            tempstack.pop();
        }

        cout << "--------------------------------------------\n";
        cout << "TOTAL AMOUNT DUE: $" << totalamount << endl;
        cout << "============================================\n";

        // clear bill after generation
        while (!billingstack.empty())
        {
            billingstack.pop();
        }
    }
};
// ==================== APPOINTMENT MANAGEMENT MODULE ====================

struct Appointment
{
    int patientId;
    int doctorId;
    string date;
    string time;
    string type;   // Regular / Emergency

    Appointment()
    {
        patientId = 0;
        doctorId = 0;
    }
};

struct EmergencyAppointment
{
    Appointment appointment;
    int severity;   // 1 (low)  10 (high)

    EmergencyAppointment()
    {
        severity = 0;
    }

    // Higher severity = higher priority
    bool operator<(const EmergencyAppointment& other) 
    const
    {
        return severity < other.severity;
    }
};

class AppointmentManager
{
private:
    queue<Appointment> regularQueue;
    priority_queue<EmergencyAppointment> emergencyQueue;

    // ---------- LOAD FROM CSV ----------
    void loadAppointmentsFromFile()
    {
        ifstream file("appointments.csv");
        if (!file.is_open())
        {
            return;
        }

        string line;
        getline(file, line); // skip header

        while (getline(file, line))
        {
            if (line.empty()) continue;

            stringstream ss(line);
            string patientId, doctorId, date, time, type, severity;

            getline(ss, patientId, ',');
            getline(ss, doctorId, ',');
            getline(ss, date, ',');
            getline(ss, time, ',');
            getline(ss, type, ',');
            getline(ss, severity, ',');

            if (type == "Emergency")
            {
                EmergencyAppointment emergency;
                //ASCII TO Integer
                emergency.appointment.patientId = atoi(patientId.c_str());
                emergency.appointment.doctorId  = atoi(doctorId.c_str());
                emergency.appointment.date      = UnescapeCSV(date);
                emergency.appointment.time      = UnescapeCSV(time);
                emergency.appointment.type      = "Emergency";
                emergency.severity              = atoi(severity.c_str());

                emergencyQueue.push(emergency);
            }
            else
            {
                Appointment regular;
                regular.patientId = atoi(patientId.c_str());
                regular.doctorId  = atoi(doctorId.c_str());
                regular.date      = UnescapeCSV(date);
                regular.time      = UnescapeCSV(time);
                regular.type      = "Regular";

                regularQueue.push(regular);
            }
        }

        file.close();
    }

    // ---------- SAVE TO CSV ----------
    void saveAppointmentsToFile()
    {
        ofstream file("appointments.csv");
        file << "PatientID,DoctorID,Date,Time,Type,Severity\n";

        priority_queue<EmergencyAppointment> tempEmergency = emergencyQueue;
        while (!tempEmergency.empty())
        {
            EmergencyAppointment e = tempEmergency.top();
            tempEmergency.pop();

            file << e.appointment.patientId << ","
                 << e.appointment.doctorId << ","
                 << EscapeCSV(e.appointment.date) << ","
                 << EscapeCSV(e.appointment.time) << ","
                 << "Emergency,"
                 << e.severity << "\n";
        }

        queue<Appointment> tempRegular = regularQueue;
        while (!tempRegular.empty())
        {
            Appointment r = tempRegular.front();
            tempRegular.pop();

            file << r.patientId << ","
                 << r.doctorId << ","
                 << EscapeCSV(r.date) << ","
                 << EscapeCSV(r.time) << ","
                 << "Regular,0\n";
        }

        file.close();
    }

public:
    AppointmentManager()
    {
        loadAppointmentsFromFile();
    }

    // ---------- REGULAR APPOINTMENT ----------
    void scheduleRegularAppointment()
    {
        Appointment appointment;

        cout << "\n=== Schedule Regular Appointment ===\n";

        cout << "Enter Patient ID: ";
        appointment.patientId = GetValidInteger();

        cout << "Enter Doctor ID: ";
        appointment.doctorId = GetValidInteger();

        cout << "Enter Date (DD-MM-YYYY): ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, appointment.date);

        cout << "Enter Time (HH:MM): ";
        getline(cin, appointment.time);

        appointment.type = "Regular";
        regularQueue.push(appointment);

        saveAppointmentsToFile();
        cout << "Regular appointment scheduled successfully.\n";
    }

    // ---------- EMERGENCY APPOINTMENT ----------
    void scheduleEmergencyAppointment()
    {
        EmergencyAppointment emergency;

        cout << "\n=== Schedule Emergency Appointment ===\n";

        cout << "Enter Patient ID: ";
        emergency.appointment.patientId = GetValidInteger();

        cout << "Enter Doctor ID: ";
        emergency.appointment.doctorId = GetValidInteger();

        cout << "Enter Date (DD-MM-YYYY): ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, emergency.appointment.date);

        cout << "Enter Time (HH:MM): ";
        getline(cin, emergency.appointment.time);

        cout << "Enter Severity (1–10): ";
        int level = GetValidInteger();
        if (level < 1) level = 1;
        if (level > 10) level = 10;

        emergency.severity = level;
        emergency.appointment.type = "Emergency";

        emergencyQueue.push(emergency);

        saveAppointmentsToFile();
        cout << "Emergency appointment scheduled successfully.\n";
    }

    // ---------- PROCESS NEXT ----------
    void processNextAppointment()
    {
        if (!emergencyQueue.empty())
        {
            EmergencyAppointment emergency = emergencyQueue.top();
            emergencyQueue.pop();

            cout << "\n=== NEXT APPOINTMENT (EMERGENCY) ===\n";
            cout << "Patient ID: " << emergency.appointment.patientId
                 << " | Doctor ID: " << emergency.appointment.doctorId
                 << " | Severity: " << emergency.severity << "/10\n";
            cout << "Date: " << emergency.appointment.date
                 << " | Time: " << emergency.appointment.time << endl;
        }
        else if (!regularQueue.empty())
        {
            Appointment regular = regularQueue.front();
            regularQueue.pop();

            cout << "\n=== NEXT APPOINTMENT (REGULAR) ===\n";
            cout << "Patient ID: " << regular.patientId
                 << " | Doctor ID: " << regular.doctorId << endl;
            cout << "Date: " << regular.date
                 << " | Time: " << regular.time << endl;
        }
        else
        {
            cout << "No appointments available.\n";
            return;
        }

        saveAppointmentsToFile();
    }

    // ---------- OVERVIEW ----------
    void showAppointmentSummary()
    {
        cout << "\n========== APPOINTMENT SUMMARY ==========\n";
        cout << "Emergency pending: " << emergencyQueue.size() << endl;
        cout << "Regular pending:   " << regularQueue.size() << endl;
    }
};

// ==================== EMERGENCY CASES MODULE ====================

struct Emergencycase
{
    int patientid;
    string reportedsymptoms;
    int criticalitylevel;   // 1 (low) → 10 (high)
    string arrivaltime;

    Emergencycase()
    {
        patientid = 0;
        criticalitylevel = 0;
    }

    // Higher criticality = higher priority
    bool operator<(const Emergencycase& other) const
    {
        return criticalitylevel < other.criticalitylevel;
    }
};

class Emergencymanager
{
private:
    priority_queue<Emergencycase> emergencycaseheap;

    // ---------- LOAD FROM CSV ----------
    void Loademergencycasesfromfile()
    {
        ifstream file("emergency_cases.csv");
        if (!file.is_open())
        {
            return;
        }

        string line;
        getline(file, line); // skip header

        while (getline(file, line))
        {
            if (line.empty()) continue;

            stringstream ss(line);
            string pid, symptoms, criticality, time;

            getline(ss, pid, ',');
            getline(ss, symptoms, ',');
            getline(ss, criticality, ',');
            getline(ss, time, ',');

            Emergencycase ec;
            ec.patientid = atoi(pid.c_str());
            ec.reportedsymptoms = UnescapeCSV(symptoms);

            int level = atoi(criticality.c_str());
            if (level < 1) level = 1;
            if (level > 10) level = 10;
            ec.criticalitylevel = level;

            ec.arrivaltime = UnescapeCSV(time);

            emergencycaseheap.push(ec);
        }

        file.close();
    }

    // ---------- SAVE TO CSV ----------
    void Saveemergencycasestofile()
    {
        ofstream file("emergency_cases.csv");
        file << "PatientID,Symptoms,Criticality,ArrivalTime\n";

        priority_queue<Emergencycase> temp = emergencycaseheap;
        while (!temp.empty())
        {
            Emergencycase ec = temp.top();
            temp.pop();

            file << ec.patientid << ","
                 << EscapeCSV(ec.reportedsymptoms) << ","
                 << ec.criticalitylevel << ","
                 << EscapeCSV(ec.arrivaltime) << "\n";
        }

        file.close();
    }

public:
    Emergencymanager()
    {
        Loademergencycasesfromfile();
    }

    // ---------- REGISTER EMERGENCY ----------
    void Registeremergencycase()
    {
        Emergencycase newcase;

        cout << "\n=== Register Emergency Case ===\n";

        cout << "Enter Patient ID: ";
        newcase.patientid = GetValidInteger();

        cout << "Enter Symptoms: ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, newcase.reportedsymptoms);

        cout << "Enter Criticality Level (1-10): ";
        int level = GetValidInteger();
        if (level < 1) level = 1;
        if (level > 10) level = 10;
        newcase.criticalitylevel = level;

        cout << "Enter Arrival Time (HH:MM): ";
        getline(cin, newcase.arrivaltime);

        emergencycaseheap.push(newcase);
        Saveemergencycasestofile();

        cout << "Emergency case registered with priority "
             << newcase.criticalitylevel << "/10\n";
    }

    // ---------- ATTEND MOST CRITICAL ----------
    void Attendnextcriticalcase()
    {
        if (emergencycaseheap.empty())
        {
            cout << "No emergency cases pending!\n";
            return;
        }

        Emergencycase mostcritical = emergencycaseheap.top();
        emergencycaseheap.pop();
        Saveemergencycasestofile();

        cout << "\n=== MOST CRITICAL PATIENT ===\n";
        cout << "Patient ID: " << mostcritical.patientid << endl;
        cout << "Criticality Level: "
             << mostcritical.criticalitylevel << "/10\n";
        cout << "Symptoms: " << mostcritical.reportedsymptoms << endl;
        cout << "Arrival Time: " << mostcritical.arrivaltime << endl;
    }

    // ---------- DISPLAY ALL ----------
    void Displayallemergencycases()
    {
        if (emergencycaseheap.empty())
        {
            cout << "No emergency cases pending!\n";
            return;
        }

        cout << "\n========== ALL EMERGENCY CASES ==========\n";
        cout << "Total Cases: " << emergencycaseheap.size() << endl;

        priority_queue<Emergencycase> tempheap = emergencycaseheap;
        int casenumber = 1;

        while (!tempheap.empty())
        {
            Emergencycase currentcase = tempheap.top();
            tempheap.pop();

            cout << casenumber++ << ". Patient ID: "
                 << currentcase.patientid
                 << " | Criticality: "
                 << currentcase.criticalitylevel << "/10\n";
        }
    }
};

// ==================== MAIN APPLICATION ====================

int main()
{
    Patientmanager patientmgr;
    Doctormanager doctormgr;
    Staffmanager staffmgr;
    Billingsystem billingsys;
    AppointmentManager appointmentsys;
    Emergencymanager emergencymgr;

    while (true)
    {
        cout << "\n=========================================\n";
        cout << "   SMART HOSPITAL MANAGEMENT SYSTEM\n";
        cout << "=========================================\n";
        cout << "  1. Patient Management\n";
        cout << "  2. Doctor Management\n";
        cout << "  3. Staff Management\n";
        cout << "  4. Billing System\n";
        cout << "  5. Appointment Scheduling\n";
        cout << "  6. Emergency Cases\n";
        cout << "  0. Exit System\n";
        cout << "Enter your choice: ";

        int mainchoice = GetValidInteger();

        switch (mainchoice)
        {
            case 1:
            {
                cout << "\n--- Patient Management ---\n";
                cout << "  1. Register New Patient\n";
                cout << "  2. Search Patient by ID\n";
                cout << "  3. Update Patient Information\n";
                cout << "  4. Remove Patient\n";
                cout << "  5. Display All Patients\n";
                cout << "Enter choice: ";

                int patientchoice = GetValidInteger();

                if (patientchoice == 1)
                {
                    patientmgr.Addnewpatient();
                }
                else if (patientchoice == 2)
                {
                    cout << "Enter Patient ID: ";
                    int searchid = GetValidInteger();

                    Patientrecord* found = patientmgr.Findpatientbyid(searchid);
                    if (found)
                        cout << "Patient Found: " << found->fullname << endl;
                    else
                        cout << "Patient not found!\n";
                }
                else if (patientchoice == 3)
                {
                    patientmgr.Updatepatientinfo();
                }
                else if (patientchoice == 4)
                {
                    patientmgr.Removepatient();
                }
                else if (patientchoice == 5)
                {
                    patientmgr.Displayallpatients();
                }
                break;
            }

            case 2:
            {
                cout << "\n--- Doctor Management ---\n";
                cout << "  1. Register New Doctor\n";
                cout << "  2. Search Doctor by ID\n";
                cout << "  3. Search by Specialization\n";
                cout << "  4. Display All Doctors\n";
                cout << "Enter choice: ";

                int doctorchoice = GetValidInteger();

                if (doctorchoice == 1)
                {
                    doctormgr.Addnewdoctor();
                }
                else if (doctorchoice == 2)
                {
                    cout << "Enter Doctor ID: ";
                    int searchid = GetValidInteger();

                    Doctorrecord* found = doctormgr.Finddoctorbyid(searchid);
                    if (found)
                        cout << "Doctor Found: " << found->fullname << endl;
                    else
                        cout << "Doctor not found!\n";
                }
                else if (doctorchoice == 3)
                {
                    doctormgr.Searchbyspecialization();
                }
                else if (doctorchoice == 4)
                {
                    doctormgr.Displayalldoctors();
                }
                break;
            }

            case 3:
            {
                cout << "\n--- Staff Management ---\n";
                cout << "  1. Register New Staff\n";
                cout << "  2. Assign Next Duty\n";
                cout << "  3. Display Duty Roster\n";
                cout << "Enter choice: ";

                int staffchoice = GetValidInteger();

                if (staffchoice == 1)
                    staffmgr.Addnewstaffmember();
                else if (staffchoice == 2)
                    staffmgr.Assignnextduty();
                else if (staffchoice == 3)
                    staffmgr.Displaydutyroster();

                break;
            }

            case 4:
            {
                cout << "\n--- Billing System ---\n";
                cout << "  1. Add Service Charge\n";
                cout << "  2. Add Medicine Charge\n";
                cout << "  3. Remove Last Item\n";
                cout << "  4. Generate Final Bill\n";
                cout << "Enter choice: ";

                int billingchoice = GetValidInteger();

                if (billingchoice == 1)
                    billingsys.Addservicecharge();
                else if (billingchoice == 2)
                    billingsys.Addmedicinecharge();
                else if (billingchoice == 3)
                    billingsys.Removelastitem();
                else if (billingchoice == 4)
                    billingsys.Generatefinalbill();

                break;
            }

            case 5:
            {
                cout << "\n--- Appointment Scheduling ---\n";
                cout << "  1. Schedule Regular Appointment\n";
                cout << "  2. Schedule Emergency Appointment\n";
                cout << "  3. Process Next Appointment\n";
                cout << "  4. Display Schedule Overview\n";
                cout << "Enter choice: ";

                int appointmentchoice = GetValidInteger();

                if (appointmentchoice == 1)
                    appointmentsys.scheduleRegularAppointment();
                else if (appointmentchoice == 2)
                    appointmentsys.scheduleEmergencyAppointment();
                else if (appointmentchoice == 3)
                    appointmentsys.processNextAppointment();
                else if (appointmentchoice == 4)
                    appointmentsys.showAppointmentSummary();

                break;
            }

            case 6:
            {
                cout << "\n--- Emergency Cases ---\n";
                cout << "  1. Register Emergency Case\n";
                cout << "  2. Attend Next Critical Case\n";
                cout << "  3. Display All Emergency Cases\n";
                cout << "Enter choice: ";

                int emergencychoice = GetValidInteger();

                if (emergencychoice == 1)
                    emergencymgr.Registeremergencycase();
                else if (emergencychoice == 2)
                    emergencymgr.Attendnextcriticalcase();
                else if (emergencychoice == 3)
                    emergencymgr.Displayallemergencycases();

                break;
            }

            case 0:
            {
                cout << "\nThank you for using the system.\n";
                return 0;
            }

            default:
                cout << "Invalid choice! Please try again.\n";
        }
    }
}
