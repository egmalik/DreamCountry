package com.example.dreamcountry;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.Adapter;
import android.widget.AdapterView;
import android.widget.CheckBox;
import android.widget.Spinner;
import android.widget.Toast;

import com.example.dreamcountry.adapters.SpinnerAdapter;
import com.example.dreamcountry.model.Country;
import com.example.dreamcountry.web.RetrofitClientInstance;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;

public class MainActivity extends AppCompatActivity implements AdapterView.OnItemSelectedListener {

    private Spinner countrySpinner;
    private String[] countries;
    private List<String> countryList;
    private List<Country> apiresponse ;
    private SpinnerAdapter adapter ;
    private CheckBox lex ;
    private CheckBox area;
    private boolean userIsInteracting;
    private int check;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);//will hide the title
        getSupportActionBar().hide(); //hide the title bar
        setContentView(R.layout.activity_main);
        bindView();
        fillCountryList();






    }

    @Override
    public void onItemSelected(AdapterView<?> parent, View arg1, int pos,long id) {
        Log.i("spinnerClicked","spinnerClicked"+ check + "and postion equel "+ pos);
        if (pos==0)return;
            Log.i("spinnerClicked", "spinnerClicked");
            Intent intent = new Intent(MainActivity.this, NearByCountries.class);
            String Borders = fillTheRequest(apiresponse.get(pos));
            intent.putExtra("TargetCountry", Borders);
            Log.i("TargetCountry", apiresponse.get(pos).getName());
            startActivity(intent);

    }

    private String fillTheRequest(Country country) {
        String apiReq= "";
        Log.i("fillTheRequest", country.getName());
        if(country.getBorders()==null) return " ";
        if(country.getBorders().size()==0) return " ";
        for (int i =0;i<country.getBorders().size();i++){
            apiReq = apiReq.concat(country.getBorders().get(i)+";");
        }
        Log.i("spinnerClicked", apiReq);
        return apiReq ;
    }

    @Override
    public void onNothingSelected(AdapterView<?> adapterView) {

    }

    private void bindView() {
        setContentView(R.layout.activity_main);
        lex = findViewById(R.id.lex);
        area = findViewById(R.id.checkboxareaSize);
        countrySpinner = findViewById(R.id.countrylist);
        countryList = new ArrayList<>();
        apiresponse = new ArrayList<Country>();
        check = -1;
    }


    private void setOnClickLisnerCheckBox(CheckBox target){
        target.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                check = -1;
                switch (view.getId()){
                    case R.id.lex:
                        if (lex.isChecked()) {
                            area.setChecked(false);
                            if (apiresponse == null) {
                                Toast.makeText(MainActivity.this, "Cant sort Without respond", Toast.LENGTH_SHORT).show();
                            }
                            for (int i =1; i < apiresponse.size(); i++) {
                                for (int j = i + 1; j < apiresponse.size(); j++) {
                                    if (apiresponse.get(i).getName().compareTo(apiresponse.get(j).getName()) > 0) {
                                        Country temp = apiresponse.get(i);
                                        apiresponse.set(i, apiresponse.get(j));
                                        apiresponse.set(j, temp);
                                    }
                                }
                            }

                            adapter = new SpinnerAdapter(MainActivity.this, R.layout.country_item, countryList, apiresponse);
                            setMyAdapter();
                            for (int i = 0; i < apiresponse.size(); i++) {
                                Log.i("sortedarray", "the index is " + i + " the country is " + apiresponse.get(i).getName());
                            }
                            Toast.makeText(MainActivity.this, "Sorted By English Size!", Toast.LENGTH_SHORT).show();
                        }
                        break;

                    case R.id.checkboxareaSize:
                        if (area.isChecked()) {
                            lex.setChecked(false);
                            if (apiresponse == null) {
                                Toast.makeText(MainActivity.this, "Cant sort Without respond", Toast.LENGTH_SHORT).show();
                            }

                            for (int i = 2; i < apiresponse.size(); i++) {
                                for (int j = i; j > 1; j--) {
                                    Log.i("showindex", "the index is " + j + "the size is " + apiresponse.size() + "and the valio is " + apiresponse.get(j).getName());
                                    CorrectTheValues(j);
                                    if (apiresponse.get(j).getArea().doubleValue() > (apiresponse.get(j - 1).getArea()).doubleValue()) {
                                        Country temp = apiresponse.get(j);
                                        apiresponse.set(j, apiresponse.get(j - 1));
                                        apiresponse.set(j - 1, temp);
                                    }
                                }
                            }

                            adapter = new SpinnerAdapter(MainActivity.this, R.layout.country_item, countryList, apiresponse);
                            setMyAdapter();
                            Toast.makeText(MainActivity.this, "Sorted By area Size!", Toast.LENGTH_SHORT).show();
                            for (int i = 0; i < apiresponse.size(); i++) {
                                Log.i("sortedarray", "the index is " + i + " the country is " + apiresponse.get(i).getName() + "and the value is " + apiresponse.get(i).getArea());
                            }
                        }
                        break;
                }
            }
        });
    }

    private void CorrectTheValues(int j) {
        if (apiresponse.get(j).getArea()==null) apiresponse.get(j).setArea((float)0);
    }


    private void fillCountryList() {
        checkConnection();

        RetrofitClientInstance ci = new RetrofitClientInstance();
        RetrofitClientInstance.getRetrofitInstance().getAllCountries().enqueue(new Callback<List<Country>>() {
            @Override
            public void onResponse(Call<List<Country>> call, retrofit2.Response<List<Country>> response) {
                if (response.isSuccessful()&&response.body()!=null){
                    Toast.makeText(MainActivity.this, "data has been received HAVE FUN!", Toast.LENGTH_SHORT).show();
                    apiresponse = response.body() ;
                    Country show = new Country();
                    show.setName("List Of Countries");
                    show.setNativeName(String.valueOf(apiresponse.size()));
                    apiresponse.add(0,show);
                    Log.i("RESPONDTOJSON",response.body().get(0).getName());
                    for (int i=0 ;i<response.body().size();i++){
                        countryList.add(response.body().get(i).getName());
                    }
                    adapter = new SpinnerAdapter(MainActivity.this, R.layout.country_item, countryList,apiresponse);
                    setMyAdapter();
                    setOnClickLisnerCheckBox(lex);
                    setOnClickLisnerCheckBox(area);
                }
            }

            @Override
            public void onFailure(Call<List<Country>> call, Throwable t) {

            }
        });

    }

    private void setMyAdapter() {
        countrySpinner.setAdapter(adapter);
        countrySpinner.setSelection(Adapter.NO_SELECTION, false);
        countrySpinner.setOnItemSelectedListener(MainActivity.this);
    }

    private void checkConnection() {
        ConnectivityManager cm = (ConnectivityManager)getApplicationContext().getSystemService(Context.CONNECTIVITY_SERVICE);
        ConnectivityManager.NetworkCallback activeNetwork = new ConnectivityManager.NetworkCallback();
        boolean isMetered = cm.isActiveNetworkMetered();
        if (isMetered==true){
            AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(MainActivity.this);
            alertDialogBuilder.setTitle("Wifi Settings");
            // set dialog message
            alertDialogBuilder
                    .setMessage("Do you want to enable WIFI ?")
                    .setCancelable(false)
                    .setPositiveButton("Yes",new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog,int id) {
                            startActivity(new Intent(WifiManager.ACTION_PICK_WIFI_NETWORK));
                            recreate();
                        }
                    })
                    .setNegativeButton("No",new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog,int id) {
                            Toast.makeText(getApplicationContext(), "please Make sure you have internet connection", Toast.LENGTH_SHORT).show();
                            finish();
                        }
                    });

            // create alert dialog
            AlertDialog alertDialog = alertDialogBuilder.create();

            // show it
            alertDialog.show();



        }


    }

}