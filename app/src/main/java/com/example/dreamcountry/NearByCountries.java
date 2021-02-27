package com.example.dreamcountry;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import com.example.dreamcountry.adapters.RecycleViewAdapter;
import com.example.dreamcountry.model.Country;
import com.example.dreamcountry.web.RetrofitClientInstance;

import java.util.List;
import java.util.Objects;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class NearByCountries extends AppCompatActivity {
    private RecyclerView nearByCountry ;
    private TextView nearBymessage ;
    private String targetCountry ;
    private RecycleViewAdapter recycleViewAdapter  ;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);//will hide the title
        getSupportActionBar().hide(); //hide the title bar
        setContentView(R.layout.activity_near_by_countries);
        bindView();
        fillCountryList();



    }

    private void fillCountryList() {
        if (targetCountry.equals(" ")){
            nearBymessage.setText("What A Chance!!, There Is No Neighborhoods For \n This Country");
        }else {
            RetrofitClientInstance ci = new RetrofitClientInstance();
            RetrofitClientInstance.getRetrofitInstance().getNearByCountryByName(targetCountry).enqueue(new Callback<List<Country>>() {
                @Override
                public void onResponse(Call<List<Country>> call, Response<List<Country>> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        nearBymessage.setVisibility(View.GONE);
                        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getApplicationContext());
                        nearByCountry.setLayoutManager(linearLayoutManager);
                        recycleViewAdapter = new RecycleViewAdapter(NearByCountries.this,response.body());
                        nearByCountry.setAdapter(recycleViewAdapter); // set the Adapter to RecyclerView
                        recycleViewAdapter.notifyDataSetChanged();
                        nearByCountry.setVisibility(View.VISIBLE);
                    }
                }

                @Override
                public void onFailure(Call<List<Country>> call, Throwable t) {
                    Toast.makeText(NearByCountries.this, "Failed To Get NeatBy Country Please Try Again", Toast.LENGTH_SHORT).show();
                    Log.i("TargetCountry", t.toString());
                    //finish();
                }

            });
        }

    }



    private void bindView() {
        nearByCountry = findViewById(R.id.nearByRecycleView);
        nearBymessage = findViewById(R.id.nearByMessage);
        targetCountry =getIntent().getStringExtra("TargetCountry");
        Log.i("TargetCountryinbindview",targetCountry);
        if (targetCountry==null){
            Toast.makeText(this, "Failed To Get Country Name", Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    public void back(View view) {
        finish();
    }
}